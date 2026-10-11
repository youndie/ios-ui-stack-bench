#!/usr/bin/env python3
"""The in-app reader against logs whose answer is written down by hand (B-14).

A reader that silently drops rows, or a hitch rule that counts jitter, produces the same CSV shape as
a correct one. These cases are built in memory, run through the reader's own functions, and compared
with values worked out on paper; `make check` runs this, and it fails when the reader is broken.

    python3 analysis/inapp_reader_control.py [-v]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inapp_reader as reader  # noqa: E402


def log(scenario="S2", hz=60, pairs=40, stalls=(), extra_marks=(), drop=(), window=1.0, gap=4.0, order=None):
    """A synthetic run: process start at 100.0, launch 100.2, first frame 100.35, list 100.5, then
    `pairs` scroll windows of `window` s separated by `gap` s, frames at exactly 1/hz throughout.
    `stalls` are (time, ms) frame intervals replacing the regular one that starts at `time`."""
    period = 1 / hz
    lines = [{"k": "header", "t": 100.0, "bundle": "b", "machine": "m", "os": "o", "processStart": 100.0}]
    marks = order or [("launch", 100.2), ("firstFrame", 100.35), ("listPopulated", 100.5), (f"scenario:{scenario}", 100.25)]
    lines += [{"k": "mark", "t": t, "name": n} for n, t in marks if n not in drop]
    lines += [{"k": "mark", "t": t, "name": n} for n, t in extra_marks]
    start = 101.0
    for i in range(pairs):
        b = start + i * (window + gap)
        lines.append({"k": "scroll", "t": b, "phase": "begin", "offset": 0.0})
        lines.append({"k": "scroll", "t": b + window, "phase": "end", "offset": 100.0})
    end = start + pairs * (window + gap) + 1
    t = 100.35
    stall_at = dict(stalls)
    while t < end:
        step = period
        for at, ms in stall_at.items():
            if t <= at < t + period:
                step = ms / 1000
        lines.append({"k": "frame", "t": t, "tt": t + period})
        t += step
    for i in range(50):
        lines.append({"k": "footprint", "t": 100 + i * 0.25, "bytes": 10_000_000 + i})
    return lines


def close(a, b, tol=1e-3):
    return a != "" and abs(a - b) <= tol


CASES = []


def case(name):
    def register(fn):
        CASES.append((name, fn))
        return fn
    return register


@case("clean 60 Hz S2: valid, no hitch")
def _():
    s = reader.summarise(log(), "S2")
    return s["valid"] == 1 and s["scroll_windows"] == 40 and close(s["hitch_time_ratio_ms_per_s"], 0) and close(s["longest_hitch_ms"], 0)


@case("one 50 ms frame in a window at 60 Hz: 33.333 ms over 40 s of windows = 0.833 ms/s")
def _():
    s = reader.summarise(log(stalls=[(101.5, 50)]), "S2")
    return close(s["longest_hitch_ms"], 50 - 1000 / 60, 0.05) and close(s["hitch_time_ratio_ms_per_s"], (50 - 1000 / 60) / 40, 0.01)


@case("a writeError line makes the run invalid: the log lost lines it cannot show")
def _():
    lines = log() + [{"k": "writeError", "t": 120.0, "failed": 3, "error": "EIO"}]
    s = reader.summarise(lines, "S2")
    return s["valid"] == 0 and "3 log writes failed" in s["reason"]


@case("a 20 ms frame at 60 Hz is jitter, not a hitch (under 1.5 frames)")
def _():
    s = reader.summarise(log(stalls=[(101.5, 20)]), "S2")
    return close(s["hitch_time_ratio_ms_per_s"], 0)


@case("a 50 ms frame between windows is not counted")
def _():
    s = reader.summarise(log(stalls=[(103.0, 50)]), "S2")
    return close(s["hitch_time_ratio_ms_per_s"], 0)


@case("120 Hz: one missed vsync (16.67 ms) is a hitch of 8.33 ms")
def _():
    s = reader.summarise(log(hz=120, stalls=[(101.5, 1000 / 60)]), "S2")
    return close(s["longest_hitch_ms"], 1000 / 120, 0.05)


@case("startup: process start to list populated 500 ms, launch to list 300 ms")
def _():
    s = reader.summarise(log(scenario="S1", pairs=0), "S1")
    return s["valid"] == 1 and close(s["process_to_list_ms"], 500) and close(s["launch_to_list_ms"], 300) and close(s["process_to_first_frame_ms"], 350)


@case("S2 with 39 flings is invalid")
def _():
    s = reader.summarise(log(pairs=39), "S2")
    return s["valid"] == 0 and "39 begin" in s["reason"]


@case("a missing listPopulated is invalid")
def _():
    return reader.summarise(log(drop=("listPopulated",)), "S2")["valid"] == 0


@case("listPopulated before firstFrame is invalid")
def _():
    order = [("launch", 100.2), ("firstFrame", 100.5), ("listPopulated", 100.35), ("scenario:S2", 100.25)]
    return reader.summarise(log(order=order), "S2")["valid"] == 0


@case("the wrong scenario marker is invalid")
def _():
    return reader.summarise(log(), "S4")["valid"] == 0


@case("S3 with 23 query markers is invalid, with 24 valid")
def _():
    q = lambda n: [("query", 110 + i) for i in range(n)]
    bad = reader.summarise(log(scenario="S3", pairs=0, extra_marks=q(23)), "S3")
    good = reader.summarise(log(scenario="S3", pairs=0, extra_marks=q(24)), "S3")
    return bad["valid"] == 0 and good["valid"] == 1


@case("S4 with 49 push/pop cycles is invalid, with 50 valid")
def _():
    d = lambda n: [(name, 110 + i + off) for i in range(n) for name, off in (("detailAppeared", 0), ("detailDisappeared", 0.5))]
    bad = reader.summarise(log(scenario="S4", pairs=0, extra_marks=d(49)), "S4")
    good = reader.summarise(log(scenario="S4", pairs=0, extra_marks=d(50)), "S4")
    return bad["valid"] == 0 and good["valid"] == 1


@case("S4 growth: the sample after the 50th exit minus the sample after the 5th")
def _():
    marks = [(name, 110 + i * 2 + off) for i in range(50) for name, off in (("detailAppeared", 0), ("detailDisappeared", 1))]
    lines = log(scenario="S4", pairs=0, extra_marks=marks)
    lines = [l for l in lines if l["k"] != "footprint"]
    lines += [{"k": "footprint", "t": 110 + i * 0.25, "bytes": 1_000_000 + i * 1000} for i in range(500)]
    s = reader.summarise(lines, "S4")
    # 5th exit at 119.0 -> sample index 36 (119.0); 50th exit at 209.0 -> index 396 (209.0)
    return s["footprint_after_cycle5_bytes"] == 1_036_000 and s["growth_cycles_5_to_50_bytes"] == 360_000


@case("thermal: the worst state the run went through, from the header and every change")
def _():
    lines = log()
    lines[0]["thermal"] = "nominal"
    lines.append({"k": "thermal", "t": 120.0, "state": "fair"})
    lines.append({"k": "thermal", "t": 121.0, "state": "nominal"})
    return reader.summarise(lines, "S2")["thermal_worst"] == "fair" and reader.summarise(log(), "S2")["thermal_worst"] == "nominal"


@case("peak footprint is the largest sample")
def _():
    return reader.summarise(log(), "S2")["peak_footprint_bytes"] == 10_000_049


def main():
    verbose = "-v" in sys.argv[1:]
    failed = 0
    for name, fn in CASES:
        ok = bool(fn())
        failed += not ok
        if verbose or not ok:
            print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    print(f"control for inapp_reader.py: {len(CASES) - failed}/{len(CASES)} cases behave")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
