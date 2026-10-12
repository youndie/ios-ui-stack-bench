#!/usr/bin/env python3
"""From the runs' summary rows to one verdict per research question (B-15).

    python3 analysis/verdicts.py <runs.csv> [--sizes sizes.csv] [--out verdicts.csv]

`runs.csv` is one row per scenario run: `device` (older | newer; only older is read, A1.7), `session`, `arm` (a-native,
b1-objc, b2-skie, b3-swift-export, c-kmp-cmp), `scenario`, `counted` (0 for the batch's warm-up run),
`valid` (from analysis/inapp_reader.py), and the reader's summary columns. `sizes.csv` is one row per
arm: `arm`, `compressed_bytes`. Standard library only; the bootstrap is seeded, so a re-run prints the
same intervals.

**The rule the brief states**, for every comparison: report the median and IQR per arm, and a
bootstrap 95 % interval; a verdict is decided on the median, and the interval must not cross the
threshold. So a component is
    green          its green condition holds for the median and for both ends of the interval
    red            its red condition holds for the median and for both ends of the interval
    inconclusive   anything else - and the verdict names the condition it missed
and a question is green only if every component is, red if any component is red.

**What each RQ compares** is in RULES below. Where the brief does not say - which interval an
absolute threshold uses, which device RQ4 and RQ5 are read on, where S4's warm-up ends, what a MB is
(research §2, I2, I3, I7) - RULES carries a **proposal** for the amendments of B-01, marked as such,
and BRIEF.md's amendments win wherever they differ. RQ1 has no sample: its sizes are deterministic
and are compared as numbers. RQ1's B - A and RQ5 are decided once per B arm, never as a best of
three (amendment A1.1).
"""
import argparse
import csv
import random
import statistics
import sys

SEED = 20261010
RESAMPLES = 10_000
MB = 1_000_000  # proposal (I15): decimal, as Apple's size reports count
B_ARMS = ("b1-objc", "b2-skie", "b3-swift-export")
# A1.7: every question is read on the older device, the iPhone XS; the newer one is not measured, and
# every verdict says so. A newer device's rows in runs.csv are ignored.
DEVICES = ("older",)
# A1.7: startup is read from App Launch with Points of Interest (analysis/xctrace_reader.py).
STARTUP = "trace_process_to_list_ms"
# A2.2: smoothness is Animation Hitches on S2p, the self-scrolling launch with no runner; memory is the
# app's own footprint on S2p, and its growth on S4p, the self-navigating launch.
SMOOTH_SCENARIO, HITCH_RATIO, LONGEST_HITCH = "S2p", "trace_hitch_time_ratio_ms_per_s", "trace_longest_hitch_ms"
MEMORY_SCENARIO, GROWTH_SCENARIO = "S2p", "S4p"


# ---------------------------------------------------------------- statistics

def quantile(xs, q):
    s = sorted(xs)
    k = (len(s) - 1) * q
    lo, hi = int(k), min(int(k) + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


def iqr(xs):
    return quantile(xs, 0.75) - quantile(xs, 0.25)


def bootstrap(stat, samples, resamples=RESAMPLES, seed=SEED):
    """Percentile interval of stat(*resampled) at 95 %, each sample resampled on its own."""
    rng = random.Random(seed)
    values = []
    for _ in range(resamples):
        values.append(stat(*[[rng.choice(s) for _ in s] for s in samples]))
    return quantile(values, 0.025), quantile(values, 0.975)


def median_diff(a, b):
    return statistics.median(b) - statistics.median(a)


def median_ratio(a, b):
    return statistics.median(b) / statistics.median(a)


# ---------------------------------------------------------------- one component

def judge(value, ci, green, red):
    """green / red / inconclusive for one estimate: the condition must hold at the median and at
    both ends of the interval (the brief: the interval must not cross the threshold)."""
    points = [value] + ([] if ci is None else list(ci))
    if all(green(p) for p in points):
        return "green"
    if all(red(p) for p in points):
        return "red"
    return "inconclusive"


class Component:
    def __init__(self, rq, arm, device, metric, estimator, value, ci, n, same, verdict, green_text, red_text):
        self.row = {
            "rq": rq, "arm": arm, "device": device, "metric": metric, "estimator": estimator,
            "value": value, "ci_low": "" if ci is None else ci[0], "ci_high": "" if ci is None else ci[1],
            "runs": n, "same_device_same_session": same, "verdict": verdict,
            "green_if": green_text, "red_if": red_text,
        }

    @property
    def verdict(self):
        return self.row["verdict"]


# ---------------------------------------------------------------- data access

def counted(rows, arm, device, scenario, metric):
    out = []
    for r in rows:
        if (r["arm"], r["device"], r["scenario"]) == (arm, device, scenario) and r["counted"] == "1" and r["valid"] == "1" and r[metric] != "":
            out.append(float(r[metric]))
    return out


def same_session(rows, device, arms):
    sessions = [{r["session"] for r in rows if r["arm"] == arm and r["device"] == device} for arm in arms]
    return "yes" if sessions and all(s == sessions[0] and len(s) == 1 for s in sessions) else "no"


def compare(rq, rows, device, scenario, metric, arm_x, est, green, red, gtext, rtext, arm_a="a-native"):
    a = counted(rows, arm_a, device, scenario, metric)
    x = counted(rows, arm_x, device, scenario, metric)
    if len(a) < 2 or len(x) < 2:
        return Component(rq, arm_x, device, metric, est, "", None, f"{len(a)}/{len(x)}", "", "not measured", gtext, rtext)
    fn = median_diff if est == "median difference" else median_ratio
    value = fn(a, x)
    ci = bootstrap(fn, [a, x])
    return Component(rq, arm_x, device, metric, est, value, ci, f"{len(a)}/{len(x)}",
                     same_session(rows, device, [arm_a, arm_x]), judge(value, ci, green, red), gtext, rtext)


def absolute(rq, rows, device, scenario, metric, arm, green, red, gtext, rtext):
    x = counted(rows, arm, device, scenario, metric)
    if len(x) < 2:
        return Component(rq, arm, device, metric, "median", "", None, f"{len(x)}", "", "not measured", gtext, rtext)
    value = statistics.median(x)
    ci = bootstrap(statistics.median, [x])
    return Component(rq, arm, device, metric, "median", value, ci, f"{len(x)}", "n/a",
                     judge(value, ci, green, red), gtext, rtext)


def maximum(rq, rows, device, scenario, metric, arm, green, red, gtext, rtext):
    x = counted(rows, arm, device, scenario, metric)
    if not x:
        return Component(rq, arm, device, metric, "max over runs", "", None, "0", "", "not measured", gtext, rtext)
    value = max(x)
    return Component(rq, arm, device, metric, "max over runs", value, None, f"{len(x)}", "n/a",
                     judge(value, None, green, red), gtext, rtext)


# ---------------------------------------------------------------- the questions

def rq1(sizes, b_arm, key="compressed_bytes"):
    # The size tools write two clean builds per arm; build 1 is the measurement. `key` is the proxy:
    # B-12's zip (`compressed_bytes`), or since A2.4 Apple's estimate (`apple_download_bytes`) and the
    # encrypted worst case (`worst_case_bytes`) of scripts/measure_download.py.
    size = {r["arm"]: float(r[key]) for r in sizes if r.get("build", "1") in ("1", 1)}
    out = []
    for arm, g, r in ((b_arm, 2, 5), ("c-kmp-cmp", 12, 20)):
        if arm not in size or "a-native" not in size:
            out.append(Component("RQ1", arm, "-", key, "difference", "", None, "-", "", "not measured", "", ""))
            continue
        d = size[arm] - size["a-native"]
        out.append(Component("RQ1", arm, "-", key, f"{arm} - a-native", d, None, "1/1", "n/a",
                             judge(d, None, lambda v, g=g: v <= g * MB, lambda v, r=r: v > r * MB), f"<= {g} MB", f"> {r} MB"))
    return out


def rq2(rows):
    # The brief names the older device.
    return [compare("RQ2", rows, "older", "S1", STARTUP, "c-kmp-cmp", "median difference",
                    lambda v: v <= 100, lambda v: v > 250, "<= +100 ms", "> +250 ms")]


def rq3(rows, metric=HITCH_RATIO):
    # Proposal (I2): an absolute threshold is held by the bootstrap interval of C's median; the
    # "no single hitch" conditions are a maximum over C's counted runs, with no interval.
    out = []
    for device in DEVICES:
        out.append(absolute("RQ3", rows, device, SMOOTH_SCENARIO, metric, "c-kmp-cmp",
                            lambda v: v < 5, lambda v: v > 10, "< 5 ms/s", "> 10 ms/s"))
        out.append(maximum("RQ3", rows, device, SMOOTH_SCENARIO, LONGEST_HITCH, "c-kmp-cmp",
                           lambda v: v < 100, lambda v: v >= 250, "< 100 ms", ">= 250 ms"))
    return out


def rq4(rows):
    # Read on DEVICES - the XS only since A1.7 (I3 had both). Peak footprint from the fling scenario
    # as the brief says - S2p since A2.2; growth after cycle 5 to after cycle 50 (I7), on S4p.
    out = []
    for device in DEVICES:
        out.append(compare("RQ4", rows, device, MEMORY_SCENARIO, "peak_footprint_bytes", "c-kmp-cmp", "median ratio",
                           lambda v: v <= 2, lambda v: v > 3, "<= 2x", "> 3x"))
        out.append(absolute("RQ4", rows, device, GROWTH_SCENARIO, "growth_cycles_5_to_50_bytes", "c-kmp-cmp",
                            lambda v: v < 5 * MB, lambda v: v >= 20 * MB, "< 5 MB", ">= 20 MB"))
    return out


def rq5(rows, b_arm, metric=HITCH_RATIO):
    # Read on DEVICES - the XS only since A1.7 (I3 had both).
    out = []
    for device in DEVICES:
        out.append(compare("RQ5", rows, device, SMOOTH_SCENARIO, metric, b_arm, "median difference",
                           lambda v: v <= 1, lambda v: v > 2, "<= +1 ms/s", "> +2 ms/s"))
        out.append(compare("RQ5", rows, device, "S1", STARTUP, b_arm, "median difference",
                           lambda v: v <= 50, lambda v: v > 150, "<= +50 ms", "> +150 ms"))
        out.append(compare("RQ5", rows, device, MEMORY_SCENARIO, "peak_footprint_bytes", b_arm, "median difference",
                           lambda v: v <= 20 * MB, lambda v: v > 50 * MB, "<= +20 MB", "> +50 MB"))
    return out


def combine(components):
    verdicts = [c.verdict for c in components]
    if "red" in verdicts:
        return "RED"
    if verdicts and all(v == "green" for v in verdicts):
        return "GREEN"
    if verdicts and all(v == "not measured" for v in verdicts):
        return "NOT MEASURED"
    missed = [f"{c.row['metric']} on {c.row['device']} ({c.verdict})" for c in components if c.verdict != "green"]
    return "INCONCLUSIVE - missed: " + "; ".join(missed)


def questions(rows, sizes):
    out = [("RQ1 " + b, rq1(sizes, b)) for b in B_ARMS] if sizes else []
    out += [("RQ2", rq2(rows)), ("RQ3", rq3(rows)), ("RQ4", rq4(rows))]
    out += [("RQ5 " + b, rq5(rows, b)) for b in B_ARMS]
    return out


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("runs")
    parser.add_argument("--sizes")
    parser.add_argument("--out")
    args = parser.parse_args()
    rows, sizes = read(args.runs), (read(args.sizes) if args.sizes else [])
    table = []
    print(f"bootstrap: {RESAMPLES} resamples, seed {SEED}, percentile 95 % interval")
    print("read on the iPhone XS only; the newer device was not measured (BRIEF.md A1.7)")
    for name, components in questions(rows, sizes):
        print(f"{name}: {combine(components)}")
        for c in components:
            r = c.row
            print(f"    {r['metric']} [{r['device']}] {r['estimator']} = {r['value']} CI ({r['ci_low']}, {r['ci_high']}) "
                  f"runs {r['runs']} same session {r['same_device_same_session']} -> {r['verdict']}")
            table.append({"question": name, **r})
    if args.out and table:
        with open(args.out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(table[0]))
            w.writeheader()
            w.writerows(table)
    return 0


if __name__ == "__main__":
    sys.exit(main())
