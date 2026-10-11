#!/usr/bin/env python3
"""The control for analysis/xctrace_reader.py: B-06's real exports (analysis/fixtures/b-06/), each
expected value read out of the raw XML with a regular expression rather than through the reader.

    python3 analysis/xctrace_reader_control.py
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xctrace_reader as x  # noqa: E402

FIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "b-06")
CASES = []


def case(name):
    def register(fn):
        CASES.append((name, fn))
        return fn
    return register


def raw(path):
    return open(os.path.join(FIX, path)).read()


def event_time(xml, name):
    return int(re.search(r'<event-time[^>]*>(\d+)</event-time>(?:(?!</row>).)*fmt="' + name + '"', xml, re.S).group(1))


@case("launch: first frame and list populated, from the first life-cycle interval's start")
def _():
    starts = [int(v) for v in re.findall(r"<row><start-time[^>]*>(\d+)</start-time>", raw("startup/life-cycle-period.xml"))]
    poi = raw("startup/PointsOfInterestEvents.xml")
    got = x.launch(os.path.join(FIX, "startup"))
    return (abs(got["trace_process_to_list_ms"] - (event_time(poi, "listPopulated") - min(starts)) / 1e6) < 1e-6
            and abs(got["trace_process_to_first_frame_ms"] - (event_time(poi, "firstFrame") - min(starts)) / 1e6) < 1e-6
            and got["trace_process_to_first_frame_ms"] < got["trace_process_to_list_ms"])


@case("hitches: the ratio is the in-window durations over the window, the window from the autoScroll steps")
def _():
    xml = raw("autoscroll-50/hitches-summary.xml")
    pairs = [(int(s) / 1e9, int(d) / 1e6) for s, d in re.findall(r"<row><start-time[^>]*>(\d+)</start-time><duration[^>]*>(\d+)</duration>", xml)]
    poi = raw("autoscroll-50/PointsOfInterestEvents.xml")
    mid = re.search(r'<os-log-metadata id="(\d+)" fmt="autoScroll">', poi).group(1)  # later rows refer to it by ref
    steps = [int(t) for t, m in re.findall(r'<row><event-time[^>]*>(\d+)</event-time>.*?<os-log-metadata (?:id|ref)="(\d+)"', poi) if m == mid]
    if len(steps) != 20:
        return False
    lo, hi = min(steps) / 1e9, max(steps) / 1e9 + 1.5
    inside = [d for s, d in pairs if lo <= s <= hi]
    got = x.hitch_summary(os.path.join(FIX, "autoscroll-50"))
    return abs(got["trace_hitch_time_ratio_ms_per_s"] - sum(inside) / (hi - lo)) < 1e-9 and abs(got["trace_longest_hitch_ms"] - max(inside)) < 1e-9


@case("hitches: the 50 ms run's longest in-window hitch is a stall (40-120 ms); the 0 ms run's is not")
def _():
    on = x.hitch_summary(os.path.join(FIX, "autoscroll-50"))["trace_longest_hitch_ms"]
    off = x.hitch_summary(os.path.join(FIX, "autoscroll-0"))["trace_longest_hitch_ms"]
    return 40 <= on <= 120 and off < 40


@case("activity: the app process's peak footprint equals the app's own largest sample; CPU time in ms")
def _():
    got = x.activity(os.path.join(FIX, "memory"))
    app = max(json.loads(l)["bytes"] for l in open(os.path.join(FIX, "memory/app.ndjson")) if json.loads(l)["k"] == "footprint")
    cpus = [int(v) for v in re.findall(r"<duration-on-core[^>]*>(\d+)</duration-on-core>", raw("memory/activity-monitor-process-live.xml"))]
    return got["trace_peak_footprint_bytes"] == app and any(abs(got["trace_cpu_total_ms"] - c / 1e6) < 1e-9 for c in cpus) \
        and 1 < got["trace_cpu_total_ms"] < 60_000


@case("a missing table reads as missing, not as zero")
def _():
    return x.launch(FIX)["trace_process_to_list_ms"] == "" and x.hitch_summary(FIX)["trace_longest_hitch_ms"] == "" \
        and x.activity(FIX)["trace_peak_footprint_bytes"] == ""


def main():
    failed = 0
    for name, fn in CASES:
        try:
            ok = bool(fn())
        except Exception as e:
            ok, name = False, f"{name} (raised {type(e).__name__}: {e})"
        failed += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    print(f"control for xctrace_reader.py: {len(CASES) - failed}/{len(CASES)} cases behave")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
