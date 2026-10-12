#!/usr/bin/env python3
"""The pilot's table (B-17): every arm's counted run of each self-driven scenario, side by side.

    python3 analysis/pilot_table.py <runs.csv> [<runs.csv> ...] [--md pilot.md]

One counted run per arm and scenario: an orientation, not a verdict. analysis/verdicts.py needs at
least two runs per arm and says "not measured" here, and rightly. The figures are the ones the
verdicts read (A1.7, A2.2): startup from App Launch on S1, smoothness from Animation Hitches on S2p,
peak footprint and CPU from the app on S2p, footprint growth over cycles 5-50 on S4p. Standard library
only.
"""
import argparse
import csv
import sys

ARMS = ["a-native", "b1-objc", "b2-skie", "b3-swift-export", "c-kmp-cmp"]
COLUMNS = [
    ("S1", "trace_process_to_list_ms", "startup, ms", 1),
    ("S2p", "trace_hitch_time_ratio_ms_per_s", "hitch time, ms/s", 1),
    ("S2p", "trace_longest_hitch_ms", "longest hitch, ms", 1),
    ("S2p", "peak_footprint_bytes", "peak footprint, MB", 1e6),
    ("S2p", "cpu_total_ms", "CPU on S2p, s", 1e3),
    ("S4p", "growth_cycles_5_to_50_bytes", "growth 5-50, MB", 1e6),
]


def table(rows):
    counted = [r for r in rows if r.get("counted") == "1" and r.get("valid") == "1"]
    out = ["| Arm | " + " | ".join(c[2] for c in COLUMNS) + " | sessions |", "|---|" + "---|" * (len(COLUMNS) + 1)]
    for arm in ARMS:
        cells, sessions = [], set()
        for scenario, key, _, scale in COLUMNS:
            vals = [float(r[key]) / scale for r in counted if r["arm"] == arm and r["scenario"] == scenario and r.get(key, "") != ""]
            sessions |= {r["session"] for r in counted if r["arm"] == arm and r["scenario"] == scenario}
            cells.append(" / ".join(f"{v:.2f}" for v in vals) if vals else "-")
        out.append(f"| {arm} | " + " | ".join(cells) + f" | {', '.join(sorted(sessions)) or '-'} |")
    return "\n".join(out)


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("runs", nargs="+")
    p.add_argument("--md")
    a = p.parse_args()
    rows = [r for path in a.runs for r in csv.DictReader(open(path))]
    text = table(rows)
    print(text)
    if a.md:
        open(a.md, "w").write("Pilot, one counted run per arm and scenario - not a verdict (B-17).\n\n" + text + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
