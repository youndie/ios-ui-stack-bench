#!/usr/bin/env python3
"""RQ0's verdict from what harness/gate.py recorded (B-06): one row per control x arm, and GATE.md's table.

    python3 analysis/gate_reader.py <gate-dir> [--gate GATE.md] [--csv gate.csv]

**The pass conditions, fixed before the gate's first recording** (committed with this file):

    stall, logger      the in-app frame log of a run with `-benchStallMs 50`: at least 90 % of the
                       injected stalls fall inside a frame interval whose hitch time (interval minus one
                       frame) is >= 25 ms; with `-benchStallMs 0`, at most 5 % do. Read on the
                       self-scrolling run and on S2 alike (A1.7).
    stall, Hitches     the Animation Hitches trace of the self-scrolling run: with the 50 ms stall, at
                       least one hitch of 40-120 ms starting within 150 ms of an injected stall, inside
                       the scrolling window (first `autoScroll` signpost to 1.5 s after the last); with
                       the 0 ms stall, no hitch >= 40 ms inside that window.
    startup            median over 5 launches with `-benchDelayListMs 200` minus median over 5 without,
                       150-250 ms - in the trace (Points of Interest `listPopulated` minus the first
                       `life-cycle-period` start) and in the app's log (`listPopulated` minus `launch`,
                       the app's earliest Swift code) alike. Not the app's process start: under
                       `xctrace --launch` the process is spawned suspended until Instruments attaches, and
                       the kernel's start time takes that wait in, 480-560 ms and varying (B-06's dry run).
    memory             median over 3 launches with `-benchAllocateMB 50` minus median over 3 without,
                       of the largest footprint, 40-60 MiB - Activity Monitor's
                       `memory-physical-footprint` of the app's process and the app's `phys_footprint`
                       samples alike.
    size               the zip proxy grows by 0.95-1.10 MiB when 1 MiB of random bytes is added.

A row is `pass`, `fail`, or `not captured` (a recording or a table missing). RQ0 is green when every
row of every arm passes; red when a metric is not captured for an arm, or C's stall is seen by
neither instrument (kill criteria 1 and 2); grey when C's stall is seen by one instrument only
(B-06, I4); otherwise not green, with the failing rows named.

Clocks: a trace counts nanoseconds from its own start; the app counts seconds of
`CACurrentMediaTime`. The two are aligned on the first `autoScroll` marker, which is in both.
Standard library only.
"""
import argparse
import csv
import glob
import json
import os
import statistics
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inapp_reader  # noqa: E402

MIB = 1 << 20
STALL_SEEN_MS = 25.0
HITCH_MIN_MS, HITCH_MAX_MS, HITCH_NEAR_S = 40.0, 120.0, 0.150
AUTOSCROLL_TAIL_S = 1.5


# ---------------------------------------------------------------- xctrace exports

def table(path):
    """Rows of one exported table as {mnemonic: (fmt, text)}, `ref`s resolved to their `id`s."""
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return None
    root = ET.parse(path).getroot()
    node = root.find(".//node")
    if node is None:
        return None
    cols = [c.find("mnemonic").text for c in node.find("schema").findall("col")]
    ids, rows = {}, []
    for r in node.findall("row"):
        row = {}
        for col, e in zip(cols, list(r)):
            for d in e.iter():
                if d.get("id"):
                    ids[d.get("id")] = (d.get("fmt"), d.text)
            row[col] = ids.get(e.get("ref")) if e.get("ref") else (e.get("fmt"), e.text)
        rows.append(row)
    return rows


def ns(cell):
    return int(cell[1])


def signposts(path, name):
    rows = table(path) or []
    return sorted(ns(r["time"]) for r in rows if r.get("name") and r["name"][1] == name)


# ---------------------------------------------------------------- app logs

def app_lines(run):
    path = os.path.join(run, "app.ndjson")
    return inapp_reader.load(path) if os.path.exists(path) else None


def stalls_seen(lines):
    """(injected stalls, of them inside a frame interval whose hitch time is >= 25 ms)."""
    frames = sorted((l["t"], l["tt"]) for l in lines if l["k"] == "frame")
    stalls = sorted(l["t"] for l in lines if l["k"] == "stall")
    seen = 0
    for t in stalls:
        for (t0, tt0), (t1, _) in zip(frames, frames[1:]):
            if t0 <= t < t1:
                if (t1 - t0) * 1000 - (tt0 - t0) * 1000 >= STALL_SEEN_MS:
                    seen += 1
                break
    return len(stalls), seen


def mark(lines, name):
    ts = sorted(l["t"] for l in lines if l["k"] == "mark" and l["name"] == name)
    return ts


# ---------------------------------------------------------------- the checks

def check_logger(run, stall):
    lines = app_lines(run)
    if not lines:
        return "not captured", "no app log", ""
    n, seen = stalls_seen(lines)
    if n == 0:
        return "not captured", "no stall in the log", ""
    share = seen / n
    ok = share >= 0.90 if stall else share <= 0.05
    return ("pass" if ok else "fail"), f"{seen}/{n} stalls on a hitch >= {STALL_SEEN_MS:.0f} ms ({share:.0%})", ">= 90 %" if stall else "<= 5 %"


def check_hitches(run, stall):
    hitches = table(os.path.join(run, "hitches-summary.xml"))
    poi = os.path.join(run, "PointsOfInterestEvents.xml")
    lines = app_lines(run)
    if hitches is None or table(poi) is None or not lines:
        return "not captured", "hitches, signposts or app log missing", ""
    app_steps = mark(lines, "autoScroll")
    trace_auto = signposts_with_message(poi, "autoScroll")
    if not trace_auto or not app_steps:
        return "not captured", f"autoScroll markers: {len(trace_auto)} in the trace, {len(app_steps)} in the app", ""
    lo, hi = trace_auto[0] / 1e9, trace_auto[-1] / 1e9 + AUTOSCROLL_TAIL_S
    offset = trace_auto[0] / 1e9 - app_steps[0]
    stalls = [l["t"] + offset for l in lines if l["k"] == "stall"]
    inside = [(ns(h["start"]) / 1e9, ns(h["duration"]) / 1e6) for h in hitches if lo <= ns(h["start"]) / 1e9 <= hi]
    long = [(s, d) for s, d in inside if d >= HITCH_MIN_MS]
    if stall:
        matched = [(s, d) for s, d in long if d <= HITCH_MAX_MS and any(abs(s - t) <= HITCH_NEAR_S for t in stalls)]
        return ("pass" if matched else "fail"), f"{len(matched)} hitches of {HITCH_MIN_MS:.0f}-{HITCH_MAX_MS:.0f} ms at an injected stall; {len(long)} >= {HITCH_MIN_MS:.0f} ms in the window", ">= 1"
    return ("pass" if not long else "fail"), f"{len(long)} hitches >= {HITCH_MIN_MS:.0f} ms in the window", "0"


def signposts_with_message(path, message):
    """Bench emits phases as the event `phase` with the phase's name as its message."""
    rows = table(path) or []
    return sorted(ns(r["time"]) for r in rows if r.get("message") and r["message"][0] == message)


def launch_ms(run):
    trace = app = None
    periods = table(os.path.join(run, "life-cycle-period.xml"))
    listed = signposts(os.path.join(run, "PointsOfInterestEvents.xml"), "listPopulated")
    if periods and listed:
        trace = (listed[0] - min(ns(p["start"]) for p in periods)) / 1e6
    lines = app_lines(run)
    if lines:
        lp, start = mark(lines, "listPopulated"), mark(lines, "launch")
        if lp and start:
            app = (lp[0] - start[0]) * 1000
    return trace, app


def peak_bytes(run):
    rows = table(os.path.join(run, "activity-monitor-process-live.xml"))
    trace = None
    if rows:
        mine = [int(r["memory-physical-footprint"][1]) for r in rows
                if r.get("process") and (r["process"][0] or "").startswith("Bench") and r.get("memory-physical-footprint")]
        trace = max(mine) if mine else None
    lines = app_lines(run)
    app = max((l["bytes"] for l in lines if l["k"] == "footprint"), default=None) if lines else None
    return trace, app


def paired(arm_dir, check, on, off, count, fn):
    """Median of `fn` over the runs with the control on, minus over the runs without, per instrument."""
    out = []
    for k in range(2):
        a = [fn(os.path.join(arm_dir, check, f"{on}-{i}"))[k] for i in range(1, count + 1)]
        b = [fn(os.path.join(arm_dir, check, f"{off}-{i}"))[k] for i in range(1, count + 1)]
        a, b = [x for x in a if x is not None], [x for x in b if x is not None]
        out.append((statistics.median(a) - statistics.median(b), len(a), len(b)) if a and b else (None, len(a), len(b)))
    return out


def rows_for(arm_dir):
    arm = os.path.basename(arm_dir)
    rows = []

    def add(metric, instrument, verdict, observed, expected, path):
        rows.append({"arm": arm, "metric": metric, "instrument": instrument, "verdict": verdict,
                     "expected": expected, "observed": observed, "log": os.path.relpath(path, os.path.dirname(os.path.dirname(arm_dir)))})

    for stall in (50, 0):
        run = os.path.join(arm_dir, "smooth-autoscroll", f"stall-{stall}")
        v, o, e = check_hitches(run, stall)
        add(f"stall {stall} ms, self-scroll", "Animation Hitches", v, o, e, run)
        v, o, e = check_logger(run, stall)
        add(f"stall {stall} ms, self-scroll", "in-app logger", v, o, e, run)
        run = os.path.join(arm_dir, "smooth-s2", f"stall-{stall}")
        v, o, e = check_logger(run, stall)
        add(f"stall {stall} ms, S2", "in-app logger", v, o, e, run)
    for (d, na, nb), inst in zip(paired(arm_dir, "startup", "delay-200", "delay-0", 5, launch_ms), ("App Launch + POI", "in-app log")):
        verdict = "not captured" if d is None else ("pass" if 150 <= d <= 250 else "fail")
        add("startup +200 ms", inst, verdict, "" if d is None else f"{d:+.0f} ms (median of {na} vs {nb})", "150-250 ms",
            os.path.join(arm_dir, "startup"))
    for (d, na, nb), inst in zip(paired(arm_dir, "memory", "alloc-50", "alloc-0", 3, peak_bytes), ("Activity Monitor", "in-app sampler")):
        verdict = "not captured" if d is None else ("pass" if 40 * MIB <= d <= 60 * MIB else "fail")
        add("memory +50 MiB", inst, verdict, "" if d is None else f"{d / MIB:+.1f} MiB (median of {na} vs {nb})", "40-60 MiB",
            os.path.join(arm_dir, "memory"))
    size = os.path.join(arm_dir, "size", "size.json")
    if os.path.exists(size):
        d = json.load(open(size))["zip_delta_bytes"] / MIB
        add("size +1 MiB", "zip proxy", "pass" if 0.95 <= d <= 1.10 else "fail", f"{d:+.3f} MiB", "0.95-1.10 MiB", os.path.dirname(size))
    else:
        add("size +1 MiB", "zip proxy", "not captured", "", "0.95-1.10 MiB", os.path.dirname(size))
    return rows


def verdict(rows):
    if not rows:
        return "NOT RUN"
    if any(r["verdict"] == "not captured" for r in rows):
        return "RED - not captured: " + "; ".join(f"{r['arm']} {r['metric']} ({r['instrument']})" for r in rows if r["verdict"] == "not captured")
    c50 = {r["instrument"]: r["verdict"] for r in rows if r["arm"] == "c-kmp-cmp" and r["metric"] == "stall 50 ms, self-scroll"}
    if c50 and all(v == "fail" for v in c50.values()):
        return "RED - C's stall seen by neither instrument"
    if c50 and len(set(c50.values())) > 1:
        return "GREY - C's stall seen by one instrument only"
    failed = [r for r in rows if r["verdict"] != "pass"]
    if not failed:
        return "GREEN"
    return "NOT GREEN - " + "; ".join(f"{r['arm']} {r['metric']} ({r['instrument']})" for r in failed)


def markdown(rows, device):
    out = [f"RQ0 on the {device}: **{verdict(rows)}**", "",
           "| Arm | Control | Instrument | Expected | Observed | Verdict | Log |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['arm']} | {r['metric']} | {r['instrument']} | {r['expected']} | {r['observed']} | {r['verdict']} | `{r['log']}` |")
    return "\n".join(out)


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("gate")
    p.add_argument("--gate-md")
    p.add_argument("--csv")
    a = p.parse_args()
    arms = sorted(d for d in glob.glob(os.path.join(a.gate, "*")) if os.path.isfile(os.path.join(d, "header.json")))
    rows = [r for d in arms for r in rows_for(d)]
    device = json.load(open(os.path.join(arms[0], "header.json")))["device"]["model"] if arms else "device"
    table_md = markdown(rows, device)
    print(table_md)
    if a.csv and rows:
        with open(a.csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    if a.gate_md:
        text = open(a.gate_md).read()
        begin, end = "<!-- BEGIN GATE TABLE (analysis/gate_reader.py) -->", "<!-- END GATE TABLE -->"
        head, rest = text.split(begin)
        _, tail = rest.split(end)
        open(a.gate_md, "w").write(f"{head}{begin}\n{table_md}\n{end}{tail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
