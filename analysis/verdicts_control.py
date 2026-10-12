#!/usr/bin/env python3
"""The verdict engine against synthetic runs whose verdict is known by construction (B-15).

Each case builds runs.csv rows in memory - a tight spread around a chosen value, so that the interval
lands where the case needs it - and checks the verdict word. `make check` runs this; it fails when a
threshold comparison is inverted.

    python3 analysis/verdicts_control.py [-v]
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verdicts as v  # noqa: E402

MB = v.MB


def runs(arm, device, scenario, values, metric, session="s1"):
    rows = [{"arm": arm, "device": device, "scenario": scenario, "session": session, "counted": "0", "valid": "1", metric: "999999"}]
    for x in values:
        rows.append({"arm": arm, "device": device, "scenario": scenario, "session": session, "counted": "1", "valid": "1", metric: str(x)})
    return rows


def spread(center, sd, n=19, seed=1):
    rng = random.Random(seed)
    return [center + rng.gauss(0, sd) for _ in range(n)]


def fill(rows):
    """Every row carries every metric column the engine reads; missing ones are empty."""
    cols = {v.STARTUP, v.HITCH_RATIO, v.LONGEST_HITCH, "peak_footprint_bytes", "growth_cycles_5_to_50_bytes"}
    for r in rows:
        for c in cols:
            r.setdefault(c, "")
    return rows


CASES = []


def case(name):
    def register(fn):
        CASES.append((name, fn))
        return fn
    return register


def rq2_with(delta, sd=5):
    rows = runs("a-native", "older", "S1", spread(400, sd), v.STARTUP)
    rows += runs("c-kmp-cmp", "older", "S1", spread(400 + delta, sd, seed=2), v.STARTUP)
    return v.rq2(fill(rows))[0]


@case("RQ2: C 50 ms slower than A, tight spread -> green")
def _():
    return rq2_with(50).verdict == "green"


@case("RQ2: C 175 ms slower -> inconclusive")
def _():
    return rq2_with(175).verdict == "inconclusive"


@case("RQ2: C 300 ms slower -> red")
def _():
    return rq2_with(300).verdict == "red"


@case("RQ2: median under +100 ms but an interval that crosses it -> inconclusive")
def _():
    c = rq2_with(90, sd=60)
    return c.row["value"] < 100 < c.row["ci_high"] and c.verdict == "inconclusive"


@case("RQ2: same session for both arms is printed as yes, two sessions as no")
def _():
    rows = runs("a-native", "older", "S1", spread(400, 5), v.STARTUP, session="s1")
    rows += runs("c-kmp-cmp", "older", "S1", spread(410, 5), v.STARTUP, session="s2")
    return rq2_with(10).row["same_device_same_session"] == "yes" and v.rq2(fill(rows))[0].row["same_device_same_session"] == "no"


def rq3_rows(ratio_older, ratio_newer, longest=60):
    rows = []
    for device, ratio in (("older", ratio_older), ("newer", ratio_newer)):
        rows += runs("c-kmp-cmp", device, v.SMOOTH_SCENARIO, spread(ratio, 0.2), v.HITCH_RATIO)
        rows += runs("c-kmp-cmp", device, v.SMOOTH_SCENARIO, [longest] * 9, v.LONGEST_HITCH)
    return fill(rows)


@case("RQ3: C at 2 ms/s on both devices, longest hitch 60 ms -> GREEN")
def _():
    return v.combine(v.rq3(rq3_rows(2, 2))) == "GREEN"


@case("RQ3, A1.7: the newer device is not read - C at 12 ms/s there leaves the XS's GREEN")
def _():
    return v.combine(v.rq3(rq3_rows(2, 12))) == "GREEN"


@case("RQ3: C at 12 ms/s on the XS -> RED")
def _():
    return v.combine(v.rq3(rq3_rows(12, 2))) == "RED"


@case("RQ3: C at 7 ms/s -> INCONCLUSIVE, naming the metric")
def _():
    return v.combine(v.rq3(rq3_rows(7, 2))).startswith(f"INCONCLUSIVE - missed: {v.HITCH_RATIO} on older")


@case("RQ3: one hitch of 260 ms in any run -> RED")
def _():
    return v.combine(v.rq3(rq3_rows(2, 2, longest=260))) == "RED"


@case("RQ1: B1 exactly +2 MB and C +12 MB -> GREEN; B2 +3 MB -> INCONCLUSIVE; B3 +6 MB -> RED")
def _():
    a = 10 * MB
    sizes = [{"arm": "a-native", "compressed_bytes": a}, {"arm": "b1-objc", "compressed_bytes": a + 2 * MB},
             {"arm": "b2-skie", "compressed_bytes": a + 3 * MB}, {"arm": "b3-swift-export", "compressed_bytes": a + 6 * MB},
             {"arm": "c-kmp-cmp", "compressed_bytes": a + 12 * MB}]
    return (v.combine(v.rq1(sizes, "b1-objc")) == "GREEN" and v.combine(v.rq1(sizes, "b2-skie")).startswith("INCONCLUSIVE")
            and v.combine(v.rq1(sizes, "b3-swift-export")) == "RED")


def rq4_rows(ratio, growth_mb):
    rows = []
    for device in v.DEVICES:
        rows += runs("a-native", device, v.MEMORY_SCENARIO, spread(100 * MB, MB), "peak_footprint_bytes")
        rows += runs("c-kmp-cmp", device, v.MEMORY_SCENARIO, spread(ratio * 100 * MB, MB, seed=2), "peak_footprint_bytes")
        rows += runs("c-kmp-cmp", device, v.GROWTH_SCENARIO, spread(growth_mb * MB, 0.2 * MB, seed=3), "growth_cycles_5_to_50_bytes")
    return fill(rows)


@case("RQ4: C at 1.8x A and 1 MB growth -> GREEN; 3.5x -> RED; 30 MB growth -> RED")
def _():
    return (v.combine(v.rq4(rq4_rows(1.8, 1))) == "GREEN" and v.combine(v.rq4(rq4_rows(3.5, 1))) == "RED"
            and v.combine(v.rq4(rq4_rows(1.8, 30))) == "RED")


@case("RQ5: B1 indistinguishable from A on all three metrics, both devices -> GREEN")
def _():
    rows = []
    for device in v.DEVICES:
        for arm, seed in (("a-native", 1), ("b1-objc", 2)):
            rows += runs(arm, device, v.SMOOTH_SCENARIO, spread(3, 0.1, seed=seed), v.HITCH_RATIO)
            rows += runs(arm, device, "S1", spread(400, 5, seed=seed), v.STARTUP)
            rows += runs(arm, device, v.MEMORY_SCENARIO, spread(100 * MB, 0.5 * MB, seed=seed), "peak_footprint_bytes")
    return v.combine(v.rq5(fill(rows), "b1-objc")) == "GREEN"


@case("an arm with no counted runs is NOT MEASURED, never green")
def _():
    return v.combine(v.rq5(fill([]), "b3-swift-export")) == "NOT MEASURED"


@case("warm-up and invalid runs are not counted")
def _():
    rows = runs("a-native", "older", "S1", [400] * 5, v.STARTUP)
    rows[1]["valid"] = "0"
    return len(v.counted(fill(rows), "a-native", "older", "S1", v.STARTUP)) == 4


@case("the bootstrap is seeded: two runs give the same interval")
def _():
    xs = spread(10, 1)
    return v.bootstrap(v.statistics.median, [xs]) == v.bootstrap(v.statistics.median, [xs])


def main():
    verbose = "-v" in sys.argv[1:]
    failed = 0
    for name, fn in CASES:
        ok = bool(fn())
        failed += not ok
        if verbose or not ok:
            print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    print(f"control for verdicts.py: {len(CASES) - failed}/{len(CASES)} cases behave")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
