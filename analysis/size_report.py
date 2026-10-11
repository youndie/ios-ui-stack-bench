#!/usr/bin/env python3
"""RQ1's report from `scripts/measure_size.py`'s sizes.csv (B-12): sizes, differences, verdicts, breakdown.

    python3 analysis/size_report.py <sizes.csv> [--md report.md]

Build 1 of each arm is the measurement; build 2 is the determinism check (`deterministic`,
`control_1mib_delta`). The verdicts are `analysis/verdicts.py`'s `rq1`, so the thresholds are the
brief's as written: B - A <= 2 MB green, > 5 MB red; C - A <= 12 MB green, > 20 MB red, on the zip
proxy, MB = 10^6 bytes (I15). One verdict per B arm, never a best of three (A1.1). The breakdown sums
the final link map by origin (analysis/linkmap.py). Standard library only.
"""
import argparse
import csv
import gzip
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import linkmap  # noqa: E402
import verdicts  # noqa: E402

ARMS = ["a-native", "b1-objc", "b2-skie", "b3-swift-export", "c-kmp-cmp"]
MAP = ["app", "kotlin", "native-in-kotlin", "swift-export", "linker", "system", "other"]
MB = verdicts.MB


def determinism(rows, arm, r):
    if r.get("deterministic") == "1":
        return "byte-identical"
    second = next((x for x in rows if x["arm"] == arm and str(x.get("build")) == "2"), None)
    if second is None:
        return "no second build"
    zip_delta = int(second["compressed_bytes"]) - int(r["compressed_bytes"])
    if second["executable_bytes"] == r["executable_bytes"]:
        return f"differ in bytes, same size; zip {zip_delta:+d} bytes"
    return f"differ in size: executable {int(second['executable_bytes']) - int(r['executable_bytes']):+d}, zip {zip_delta:+d} bytes"


def report(rows, maps=None):
    first = {r["arm"]: r for r in rows if str(r.get("build")) == "1"}
    out = ["| Arm | .app bytes | zip -9 bytes | zip - A | Main executable | Two clean builds | 1 MiB control |",
           "|---|---|---|---|---|---|---|"]
    a = first.get("a-native")
    for arm in ARMS:
        r = first.get(arm)
        if not r:
            out.append(f"| {arm} | not measured | | | | | |")
            continue
        diff = "" if not a or arm == "a-native" else f"{(int(r['compressed_bytes']) - int(a['compressed_bytes'])) / MB:+.2f} MB"
        out.append(f"| {arm} | {int(r['uncompressed_bytes']):,} | {int(r['compressed_bytes']):,} | {diff} | {int(r['executable_bytes']):,} | "
                   f"{determinism(rows, arm, r)} | "
                   f"{int(r['control_1mib_delta']) / (1 << 20):+.3f} MiB |")
    out += ["", "RQ1, one verdict per arm against A:", ""]
    for b in verdicts.B_ARMS:
        for c in verdicts.rq1(rows, b):
            row = c.row
            if row["arm"] == "c-kmp-cmp" and b != verdicts.B_ARMS[0]:
                continue
            value = "" if row["value"] == "" else f"{row['value'] / MB:+.2f} MB"
            out.append(f"- **{row['arm']} - a-native = {value}**: {row['verdict']} (green {row['green_if']}, red {row['red_if']})")
    out += ["", "The main executable by origin, from the final link map of build 1 (bytes), classified by",
            "analysis/linkmap.py when this report is generated:", "",
            "| Arm | " + " | ".join(MAP) + " | outside the map's symbols |", "|---|" + "---|" * (len(MAP) + 1)]
    for arm in ARMS:
        r = first.get(arm)
        path = maps and os.path.join(maps, f"{arm}.linkmap.txt.gz")
        if not r:
            continue
        if path and os.path.exists(path):
            with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
                _, cats = linkmap.parse(f)
        else:
            cats = {k: int(r["map_" + k]) for k in MAP}
        rest = int(r["executable_bytes"]) - sum(cats.values())
        out.append(f"| {arm} | " + " | ".join(f"{cats.get(k, 0):,}" for k in MAP) + f" | {rest:,} |")
    return "\n".join(out)


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("sizes")
    p.add_argument("--md")
    p.add_argument("--linkmaps", help="directory of <arm>.linkmap.txt.gz; without it, sizes.csv's map_ columns")
    a = p.parse_args()
    rows = list(csv.DictReader(open(a.sizes)))
    text = report(rows, a.linkmaps)
    print(text)
    if a.md:
        open(a.md, "w").write(text + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
