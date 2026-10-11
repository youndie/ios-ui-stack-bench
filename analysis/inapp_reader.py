#!/usr/bin/env python3
"""Turn one run's in-app log (apps/common/Instrumentation/Bench.swift) into CSVs and a summary row.

    python3 analysis/inapp_reader.py <log.ndjson> --scenario S2 --out <dir>

Writes <dir>/marks.csv, frames.csv, footprint.csv, scroll.csv, stalls.csv and summary.csv (one row),
and prints the summary. Standard library only. Every number a verdict could rest on comes out of
here or out of the Instruments readers, never out of a hand calculation (brief, Runs and statistics).

**Validity.** A run is `valid` only if its log says the scenario happened as specified; otherwise the
summary carries `valid=0` and the reason, and the analysis drops it - it is not shortened, filled in
or repaired (B-13, B-14):
    every run    a header; `launch`, `firstFrame`, `listPopulated` once each, in that order;
                 `scenario:<name>` once
    S2           40 scroll transitions to `begin` and 40 to `end`, strictly alternating, begin first
    S3           24 `query` markers (12 keys typed, 12 deleted)
    S4           50 `detailAppeared` and 50 `detailDisappeared`, alternating, appeared first

**The logger's hitch accounting** - defined here before any number exists (research §2, I4), and
secondary to Instruments' Animation Hitches, which is the brief's instrument:
    frame interval   the time between two consecutive CADisplayLink callbacks, t[i] - t[i-1]
    expected         that callback's frame duration, tt[i-1] - t[i-1] (8.3 ms at 120 Hz, 16.7 at 60)
    hitch            an interval longer than 1.5 x expected - at least one vsync missed; jitter
                     inside half a frame is not a hitch
    hitch time       interval - expected, for each hitch
    hitch time ratio the sum of hitch time inside the scroll windows (S2: from each `begin` to its
                     `end`), in ms, divided by the windows' total length in s: ms/s, Apple's unit
    longest hitch    the largest single hitch time inside those windows
It measures when the main thread got to run a frame callback, not when a frame reached the display;
a stall that blocks the main thread shows in both, a render-server hitch only in Instruments.

**RQ4's growth over S4** - the brief's "growth over 50 push/pop cycles after warm-up" leaves the
warm-up's end open (research §2, I7). Proposed for B-01, and implemented here until it decides:
    after cycle n   the first footprint sample at or after the n-th `detailDisappeared`
    growth          after cycle 50 minus after cycle 5, in bytes
"""
import argparse
import csv
import json
import math
import os
import sys

EXPECTED_COUNTS = {"S2": ("scroll", 40), "S3": ("query", 24), "S4": ("detail", 50)}


def load(path):
    lines = []
    with open(path, encoding="utf-8") as f:
        for number, raw in enumerate(f, 1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                lines.append(json.loads(raw))
            except json.JSONDecodeError as e:
                raise SystemExit(f"{path}:{number}: not JSON ({e}) - a log is never repaired")
    return lines


def percentile(values, p):
    if not values:
        return float("nan")
    ordered = sorted(values)
    k = (len(ordered) - 1) * p / 100
    lo, hi = math.floor(k), math.ceil(k)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (k - lo)


def validity(lines, scenario):
    headers = [l for l in lines if l["k"] == "header"]
    if len(headers) != 1:
        return f"{len(headers)} headers"
    failed = [l for l in lines if l["k"] == "writeError"]
    if failed:
        return f"{sum(l['failed'] for l in failed)} log writes failed: {failed[0]['error']}"
    marks = sorted((l for l in lines if l["k"] == "mark"), key=lambda l: l["t"])
    names = [m["name"] for m in marks]
    fixed = [n for n in names if n in ("launch", "firstFrame", "listPopulated")]
    if fixed != ["launch", "firstFrame", "listPopulated"]:
        return f"launch markers {fixed}"
    if names.count(f"scenario:{scenario}") != 1:
        return f"scenario:{scenario} logged {names.count(f'scenario:{scenario}')} times"
    if scenario == "S2":
        phases = [l["phase"] for l in sorted((l for l in lines if l["k"] == "scroll"), key=lambda l: l["t"])]
        if phases != ["begin", "end"] * 40:
            return f"scroll transitions {phases.count('begin')} begin / {phases.count('end')} end, not 40 alternating pairs"
    if scenario == "S3" and names.count("query") != 24:
        return f"{names.count('query')} query markers, not 24"
    if scenario == "S4":
        detail = [n for n in names if n in ("detailAppeared", "detailDisappeared")]
        if detail != ["detailAppeared", "detailDisappeared"] * 50:
            return f"{detail.count('detailAppeared')} detail appearances / {detail.count('detailDisappeared')} disappearances, not 50 alternating"
    return ""


def windows(lines, scenario):
    """The intervals the smoothness numbers are computed over: S2's scroll windows."""
    if scenario != "S2":
        return []
    scroll = sorted((l for l in lines if l["k"] == "scroll"), key=lambda l: l["t"])
    return [(b["t"], e["t"]) for b, e in zip(scroll[::2], scroll[1::2]) if b["phase"] == "begin" and e["phase"] == "end"]


def frame_rows(lines):
    frames = sorted((l for l in lines if l["k"] == "frame"), key=lambda l: l["t"])
    rows = []
    for prev, cur in zip(frames, frames[1:]):
        interval = (cur["t"] - prev["t"]) * 1000
        expected = (prev["tt"] - prev["t"]) * 1000
        hitch = interval - expected if expected > 0 and interval > 1.5 * expected else 0.0
        rows.append({"t": cur["t"], "interval_ms": interval, "expected_ms": expected, "hitch_ms": hitch})
    return rows


def inside(t, spans):
    return any(a <= t <= b for a, b in spans)


def summarise(lines, scenario):
    header = next(l for l in lines if l["k"] == "header") if any(l["k"] == "header" for l in lines) else {}
    reason = validity(lines, scenario)
    marks = {m["name"]: m["t"] for m in lines if m["k"] == "mark" and m["name"] in ("launch", "firstFrame", "listPopulated")}
    rows = frame_rows(lines)
    spans = windows(lines, scenario)
    in_window = [r for r in rows if inside(r["t"], spans)] if spans else []
    window_s = sum(b - a for a, b in spans)
    hitch_ms = sum(r["hitch_ms"] for r in in_window)
    footprint = [l["bytes"] for l in lines if l["k"] == "footprint"]
    over = [r for r in in_window if r["interval_ms"] > 1.5 * r["expected_ms"] > 0]
    start = header.get("processStart")
    growth = growth_s4(lines) if scenario == "S4" else ("", "", "")
    thermal = [l["state"] for l in sorted((l for l in lines if l["k"] == "thermal"), key=lambda l: l["t"])]
    return {
        "bundle": header.get("bundle", ""),
        "battery": header.get("battery", ""),
        "low_power": int(bool(header.get("lowPower"))) if header else "",
        "thermal_start": header.get("thermal", ""),
        "thermal_worst": worst_thermal([header.get("thermal", "nominal")] + thermal) if header else "",
        "machine": header.get("machine", ""),
        "os": header.get("os", ""),
        "scenario": scenario,
        "valid": 0 if reason else 1,
        "reason": reason,
        "process_to_first_frame_ms": (marks["firstFrame"] - start) * 1000 if start and "firstFrame" in marks else "",
        "process_to_list_ms": (marks["listPopulated"] - start) * 1000 if start and "listPopulated" in marks else "",
        "launch_to_list_ms": (marks["listPopulated"] - marks["launch"]) * 1000 if {"launch", "listPopulated"} <= marks.keys() else "",
        "peak_footprint_bytes": max(footprint) if footprint else "",
        "scroll_windows": len(spans),
        "scroll_seconds": window_s,
        "frames_in_windows": len(in_window),
        "hitch_time_ratio_ms_per_s": hitch_ms / window_s if window_s > 0 else "",
        "longest_hitch_ms": max((r["hitch_ms"] for r in in_window), default=0.0) if spans else "",
        "frames_over_budget_pct": 100 * len(over) / len(in_window) if in_window else "",
        "frame_p50_ms": percentile([r["interval_ms"] for r in in_window], 50) if in_window else "",
        "frame_p95_ms": percentile([r["interval_ms"] for r in in_window], 95) if in_window else "",
        "frame_p99_ms": percentile([r["interval_ms"] for r in in_window], 99) if in_window else "",
        "footprint_after_cycle5_bytes": growth[0],
        "footprint_after_cycle50_bytes": growth[1],
        "growth_cycles_5_to_50_bytes": growth[2],
    }


THERMAL_ORDER = ["nominal", "fair", "serious", "critical"]


def worst_thermal(states):
    known = [s for s in states if s in THERMAL_ORDER]
    return max(known, key=THERMAL_ORDER.index) if known else "unknown"


def growth_s4(lines):
    gone = sorted(l["t"] for l in lines if l["k"] == "mark" and l["name"] == "detailDisappeared")
    samples = sorted((l["t"], l["bytes"]) for l in lines if l["k"] == "footprint")

    def after(t):
        return next((b for ts, b in samples if ts >= t), None)

    if len(gone) < 50:
        return ("", "", "")
    five, fifty = after(gone[4]), after(gone[49])
    if five is None or fifty is None:
        return ("", "", "")
    return (five, fifty, fifty - five)


def write_csv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow(row)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("log")
    parser.add_argument("--scenario", required=True, choices=["S1", "S2", "S3", "S4"])
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    lines = load(args.log)
    os.makedirs(args.out, exist_ok=True)
    kinds = {k: [l for l in lines if l["k"] == k] for k in ("mark", "footprint", "scroll", "stall")}
    write_csv(os.path.join(args.out, "marks.csv"), kinds["mark"], ["t", "name"])
    write_csv(os.path.join(args.out, "footprint.csv"), kinds["footprint"], ["t", "bytes"])
    write_csv(os.path.join(args.out, "scroll.csv"), kinds["scroll"], ["t", "phase", "offset", "first", "firstOffsetPx", "last"])
    write_csv(os.path.join(args.out, "stalls.csv"), kinds["stall"], ["t", "ms", "actual"])
    write_csv(os.path.join(args.out, "frames.csv"), frame_rows(lines), ["t", "interval_ms", "expected_ms", "hitch_ms"])
    summary = summarise(lines, args.scenario)
    write_csv(os.path.join(args.out, "summary.csv"), [summary], list(summary))
    for key, value in summary.items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
