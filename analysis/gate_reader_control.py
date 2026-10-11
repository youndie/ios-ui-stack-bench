#!/usr/bin/env python3
"""The control for analysis/gate_reader.py: real exports with answers read another way, and cases built
so that only a correct reader passes them.

    python3 analysis/gate_reader_control.py

The fixtures under analysis/fixtures/b-06/ are exports of B-06's dry run of arm A on the iPhone XS
(scratchpad, before the gate's first recording): Animation Hitches and Points of Interest of the
self-scrolling run at 50 ms and 0 ms, App Launch and Points of Interest of one launch, Activity
Monitor of one launch with 50 MiB allocated. The app logs beside them keep every line but frames
(and footprint samples where the case does not read them). They are fixtures, not results.
Where a case needs an expected number, it reads it out of the raw XML with a regular expression,
not through the reader's own parser.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gate_reader as g  # noqa: E402

FIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "b-06")
CASES = []


def case(name):
    def register(fn):
        CASES.append((name, fn))
        return fn
    return register


def raw(path):
    return open(os.path.join(FIX, path)).read()


@case("the Points of Interest export holds the 20 autoScroll steps the app logged")
def _():
    xml = raw("autoscroll-50/PointsOfInterestEvents.xml")
    by_regex = len(re.findall(r'<os-log-metadata id="\d+" fmt="autoScroll">', xml)) + len(re.findall(r"<os-log-metadata ref=", xml))
    return len(g.signposts_with_message(os.path.join(FIX, "autoscroll-50/PointsOfInterestEvents.xml"), "autoScroll")) == 20 == by_regex


@case("hitch durations are read in raw nanoseconds, not from their display strings")
def _():
    rows = g.table(os.path.join(FIX, "autoscroll-50/hitches-summary.xml"))
    first = re.search(r"<row><start-time[^>]*>(\d+)</start-time><duration[^>]*>(\d+)</duration>", raw("autoscroll-50/hitches-summary.xml"))
    return rows and g.ns(rows[0]["duration"]) == int(first.group(2)) and g.ns(rows[0]["start"]) == int(first.group(1))


@case("50 ms stall, self-scroll: Hitches has hitches at injected stalls - pass")
def _():
    v, observed, _ = g.check_hitches(os.path.join(FIX, "autoscroll-50"), 50)
    return v == "pass" and observed.startswith("3 hitches")


@case("0 ms stall, self-scroll: no hitch >= 40 ms in the window - pass")
def _():
    v, observed, _ = g.check_hitches(os.path.join(FIX, "autoscroll-0"), 0)
    return v == "pass" and observed.startswith("0 hitches")


@case("the 0 ms run read as if it carried the 50 ms stall fails: nothing there to see")
def _():
    return g.check_hitches(os.path.join(FIX, "autoscroll-0"), 50)[0] == "fail"


@case("startup in the trace: listPopulated minus the first life-cycle interval, as the raw XML gives it")
def _():
    starts = [int(x) for x in re.findall(r"<row><start-time[^>]*>(\d+)</start-time>", raw("startup/life-cycle-period.xml"))]
    poi = raw("startup/PointsOfInterestEvents.xml")
    listed = int(re.search(r'<event-time[^>]*>(\d+)</event-time>(?:(?!</row>).)*fmt="listPopulated"', poi, re.S).group(1))
    trace, _ = g.launch_ms(os.path.join(FIX, "startup"))
    return abs(trace - (listed - min(starts)) / 1e6) < 1e-6


@case("startup in the app's log: listPopulated minus launch, not minus the process start")
def _():
    import json
    lines = [json.loads(l) for l in open(os.path.join(FIX, "startup/app.ndjson"))]
    marks = {l["name"]: l["t"] for l in lines if l["k"] == "mark"}
    _, app = g.launch_ms(os.path.join(FIX, "startup"))
    return abs(app - (marks["listPopulated"] - marks["launch"]) * 1000) < 1e-6


@case("memory in the trace: the Bench process's footprint, within 10 % of the app's own largest sample")
def _():
    trace, app = g.peak_bytes(os.path.join(FIX, "memory"))
    every = [int(x) for x in re.findall(r"<size-in-bytes[^>]*>(\d+)</size-in-bytes>", raw("memory/activity-monitor-process-live.xml"))]
    return trace is not None and trace in every and trace > 50 << 20 and abs(trace - app) / app < 0.10


def frames(gaps, stall_at):
    t, out = 100.0, []
    for gap in gaps:
        out.append({"k": "frame", "t": t, "tt": t + 1 / 60})
        t += gap
    out.append({"k": "frame", "t": t, "tt": t + 1 / 60})
    return out + [{"k": "stall", "t": s, "ms": 50} for s in stall_at]


@case("a stall inside a 66 ms frame interval is seen; one inside a regular frame is not")
def _():
    lines = frames([1 / 60] * 10 + [0.066] + [1 / 60] * 10, [100 + 10 / 60 + 0.001, 100 + 2 / 60 + 0.001])
    return g.stalls_seen(lines) == (2, 1)


def row(arm, metric, instrument, verdict):
    return {"arm": arm, "metric": metric, "instrument": instrument, "verdict": verdict}


@case("verdict: C's stall seen by one instrument only is GREY, by neither is RED")
def _():
    m = "stall 50 ms, self-scroll"
    grey = g.verdict([row("c-kmp-cmp", m, "Animation Hitches", "fail"), row("c-kmp-cmp", m, "in-app logger", "pass")])
    red = g.verdict([row("c-kmp-cmp", m, "Animation Hitches", "fail"), row("c-kmp-cmp", m, "in-app logger", "fail")])
    return grey.startswith("GREY") and red.startswith("RED")


@case("verdict: a metric not captured is RED; all passing is GREEN")
def _():
    nc = g.verdict([row("a-native", "size +1 MiB", "zip proxy", "not captured")])
    ok = g.verdict([row("a-native", "size +1 MiB", "zip proxy", "pass")])
    return nc.startswith("RED") and ok == "GREEN"


def main():
    failed = 0
    for name, fn in CASES:
        try:
            ok = bool(fn())
        except Exception as e:  # a crash is a failure of the case, named
            ok, name = False, f"{name} (raised {type(e).__name__}: {e})"
        if not ok:
            failed += 1
            print(f"  FAIL {name}")
        else:
            print(f"  ok   {name}")
    print(f"control for gate_reader.py: {len(CASES) - failed}/{len(CASES)} cases behave")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
