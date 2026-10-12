#!/usr/bin/env python3
"""The control for analysis/dryrun_reader.py: synthetic dry runs whose report is known (B-16).

    python3 analysis/dryrun_reader_control.py
"""
import csv
import json
import os
import random
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dryrun_reader as dr  # noqa: E402


def session(offset_odd=0.0, sd=5.0):
    rng = random.Random(7)
    rows = []
    for scenario, n in (("S1", 20), ("S2p", 10), ("S4p", 10)):
        for run in range(n):
            shift = offset_odd if run % 2 else 0.0
            rows.append({"device": "older", "session": "ruler", "arm": "a-native", "scenario": scenario, "run": str(run), "attempt": "1",
                         "counted": "1" if run else "0", "valid": "1", "decision": "count", "why": "", "thermal_worst": "nominal",
                         "trace_process_to_list_ms": str(400 + shift + rng.gauss(0, sd)) if scenario == "S1" else "",
                         "trace_hitch_time_ratio_ms_per_s": str(1.0 + rng.gauss(0, 0.05)) if scenario == "S2p" else "",
                         "peak_footprint_bytes": str(40e6 + rng.gauss(0, 1e5)) if scenario == "S2p" else "",
                         "growth_cycles_5_to_50_bytes": str(1e5) if scenario == "S4p" else "",
                         "trace_longest_hitch_ms": "20" if scenario == "S2p" else ""})
    return rows


def write_runs(d, rows):
    os.makedirs(os.path.join(d, "ruler"), exist_ok=True)
    with open(os.path.join(d, "ruler", "runs.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def idle(d, mode, i, cpu, foot):
    where = os.path.join(d, "runner", f"{mode}-{i}")
    os.makedirs(where, exist_ok=True)
    with open(os.path.join(where, "app.ndjson"), "w") as f:
        for k in range(4):
            f.write(json.dumps({"k": "footprint", "t": 100 + k, "bytes": foot - 1000 * (3 - k), "cpuMs": cpu * (k + 1) / 4}) + "\n")


def verdict_of(report, question):
    row = next(l for l in report.splitlines() if l.startswith(f"| {question}"))
    return row.split("|")[7].strip()


CASES = []


def case(name):
    def register(fn):
        CASES.append((name, fn))
        return fn
    return register


@case("A against itself, halves alike: the ruler's RQ2 is green")
def _(d):
    write_runs(d, session())
    return verdict_of(dr.report(d), "RQ2") == "green"


@case("the odd half 300 ms slower: RQ2's ruler is red - the halves are what is compared")
def _(d):
    write_runs(d, session(offset_odd=300))
    return verdict_of(dr.report(d), "RQ2") == "red"


@case("a spread wider than the bar: RQ2's ruler is inconclusive, not green")
def _(d):
    write_runs(d, session(sd=250))
    return verdict_of(dr.report(d), "RQ2") == "inconclusive"


@case("runner: a 5 % CPU shift passes kill criterion 5, a 20 % shift fails it")
def _(d):
    for i in range(1, 6):
        idle(d, "with", i, 1050, 40_000_000)
        idle(d, "without", i, 1000, 40_000_000)
    ok = [r for r in dr.runner(d) if r["metric"] == "cpu_total_ms"][0]["verdict"] == "pass"
    for i in range(1, 6):
        idle(d, "with", i, 1200, 40_000_000)
    bad = [r for r in dr.runner(d) if r["metric"] == "cpu_total_ms"][0]["verdict"].startswith("fail")
    return ok and bad


@case("no recordings: every part says not measured")
def _(d):
    text = dr.report(d)
    return "| not measured |" in text and "not measured" in text.split("Kill criterion 5")[1]


def main():
    failed = 0
    for name, fn in CASES:
        with tempfile.TemporaryDirectory() as d:
            try:
                ok = bool(fn(d))
            except Exception as e:
                ok, name = False, f"{name} (raised {type(e).__name__}: {e})"
        failed += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    print(f"control for dryrun_reader.py: {len(CASES) - failed}/{len(CASES)} cases behave")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
