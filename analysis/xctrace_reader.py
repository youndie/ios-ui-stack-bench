#!/usr/bin/env python3
"""Readers of the tables `xctrace export` writes, as the iPhone XS produced them (B-06, B-24).

Each reader takes one recording's directory - the tables exported verbatim as `<schema>.xml` - and
returns numbers. Used by analysis/gate_reader.py (RQ0's controls) and harness/session.py (the
sessions). Their control is analysis/gate_reader_control.py and analysis/xctrace_reader_control.py,
against real exports of B-06's dry run.

    life-cycle-period + PointsOfInterestEvents   App Launch with Points of Interest (A1.7)
        trace_process_to_first_frame_ms   the `firstFrame` signpost minus the first life-cycle
                                          interval's start - the process's first moment in the trace
        trace_process_to_list_ms          the same for `listPopulated` - RQ2's and RQ5's startup
    hitches-summary + PointsOfInterestEvents     Animation Hitches with Points of Interest (A1.7)
        the scrolling window              the first `autoScroll` step to 1.5 s after the last
        trace_hitch_time_ratio_ms_per_s   the hitches' durations inside the window over its length
        trace_longest_hitch_ms            the longest of them
    activity-monitor-process-live                Activity Monitor (A1.7, A2.1)
        trace_peak_footprint_bytes        the largest `memory-physical-footprint` of the app's process
        trace_cpu_total_ms                its largest `cpu-total`, the process's CPU time

Times in a trace are nanoseconds from its start; durations and sizes are read from the raw values,
never from their display strings. Standard library only.
"""
import os
import xml.etree.ElementTree as ET

AUTOSCROLL_TAIL_S = 1.5


def table(path):
    """Rows of one exported table as {mnemonic: (fmt, text)}, `ref`s resolved to their `id`s; None when
    the file is missing, empty, or holds no table."""
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return None
    node = ET.parse(path).getroot().find(".//node")
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
    """Times of the signpost events of that name, ns, in order."""
    return sorted(ns(r["time"]) for r in table(path) or [] if r.get("name") and r["name"][1] == name)


def signposts_with_message(path, message):
    """Bench emits phases as the event `phase` with the phase's name as its message (in `fmt`)."""
    return sorted(ns(r["time"]) for r in table(path) or [] if r.get("message") and r["message"][0] == message)


def launch(run):
    out = {"trace_process_to_first_frame_ms": "", "trace_process_to_list_ms": ""}
    periods = table(os.path.join(run, "life-cycle-period.xml"))
    poi = os.path.join(run, "PointsOfInterestEvents.xml")
    if not periods:
        return out
    start = min(ns(p["start"]) for p in periods)
    for key, name in (("trace_process_to_first_frame_ms", "firstFrame"), ("trace_process_to_list_ms", "listPopulated")):
        t = signposts(poi, name)
        if t:
            out[key] = (t[0] - start) / 1e6
    return out


def autoscroll_window(run):
    steps = signposts_with_message(os.path.join(run, "PointsOfInterestEvents.xml"), "autoScroll")
    return (steps[0] / 1e9, steps[-1] / 1e9 + AUTOSCROLL_TAIL_S) if steps else None


def hitches(run):
    """(start s, duration ms) of every hitch in the recording."""
    rows = table(os.path.join(run, "hitches-summary.xml"))
    return None if rows is None else [(ns(h["start"]) / 1e9, ns(h["duration"]) / 1e6) for h in rows]


def hitch_summary(run):
    out = {"trace_hitch_time_ratio_ms_per_s": "", "trace_longest_hitch_ms": "", "trace_window_s": ""}
    window, found = autoscroll_window(run), hitches(run)
    if window is None or found is None:
        return out
    lo, hi = window
    inside = [d for s, d in found if lo <= s <= hi]
    out.update(trace_hitch_time_ratio_ms_per_s=sum(inside) / (hi - lo), trace_longest_hitch_ms=max(inside, default=0.0),
               trace_window_s=hi - lo)
    return out


def activity(run, process_prefix="Bench"):
    out = {"trace_peak_footprint_bytes": "", "trace_cpu_total_ms": ""}
    rows = table(os.path.join(run, "activity-monitor-process-live.xml"))
    mine = [r for r in rows or [] if r.get("process") and (r["process"][0] or "").startswith(process_prefix)]
    foot = [int(r["memory-physical-footprint"][1]) for r in mine if r.get("memory-physical-footprint")]
    cpu = [int(r["cpu-total"][1]) / 1e6 for r in mine if r.get("cpu-total")]
    if foot:
        out["trace_peak_footprint_bytes"] = max(foot)
    if cpu:
        out["trace_cpu_total_ms"] = max(cpu)
    return out
