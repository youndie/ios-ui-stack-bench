#!/usr/bin/env python3
"""RQ1's report from scripts/measure_download.py's download.csv (B-31, A2.4).

    python3 analysis/download_report.py <download.csv> [--md report.md]

Per arm (build 1 is the measurement, build 2 the reproducibility check): Apple's download estimate,
the install size, the encrypted worst case, and B-12's zip proxy of the same bytes. Then RQ1 twice,
by analysis/verdicts.py's rule (B - A <= 2 MB green, > 5 MB red; C - A <= 12 MB green, > 20 MB red;
MB = 10^6). **The verdict is the one on Apple's estimate.** The worst case's verdict is printed beside it
and decides nothing (A2.4). Standard library only.
"""
import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verdicts  # noqa: E402

ARMS = [("a-native", "A"), ("b1-objc", "B1"), ("b2-skie", "B2"), ("b3-swift-export", "B3"), ("c-kmp-cmp", "C")]
MB = verdicts.MB
LABEL = {"apple_download_bytes": "Apple's download estimate (decides RQ1)", "worst_case_bytes": "encrypted worst case (printed beside, decides nothing)"}


def reproduce(rows, arm, key):
    one = [r for r in rows if r["arm"] == arm]
    vals = {r["build"]: int(r[key]) for r in one}
    if len(vals) < 2:
        return "one build"
    d = vals.get("2", 0) - vals.get("1", 0)
    return "identical" if d == 0 else f"{d:+d} bytes"


def verdict_lines(rows, key):
    out = []
    for b in verdicts.B_ARMS + ("c-kmp-cmp",):
        comps = verdicts.rq1(rows, b if b != "c-kmp-cmp" else verdicts.B_ARMS[0], key)
        c = next(x for x in comps if x.row["arm"] == b)
        r = c.row
        value = "" if r["value"] == "" else f"{r['value'] / MB:+.2f} MB"
        out.append(f"- {r['arm']} - a-native = **{value}**: {r['verdict']} (green {r['green_if']}, red {r['red_if']})")
    return out


def report(rows):
    first = {r["arm"]: r for r in rows if str(r["build"]) == "1"}
    a = first.get("a-native")
    out = ["| Arm | Apple's download estimate | minus A | Installed | Encrypted worst case | minus A | zip -9 of the same bytes | Executable's encrypted range | Second build, Apple's estimate |",
           "|---|---|---|---|---|---|---|---|---|"]
    for arm, n in ARMS:
        r = first.get(arm)
        if not r:
            out.append(f"| {n} | not measured | | | | | | | |")
            continue
        da = "" if arm == "a-native" or not a else f"{(int(r['apple_download_bytes']) - int(a['apple_download_bytes'])) / MB:+.2f} MB"
        dw = "" if arm == "a-native" or not a else f"{(int(r['worst_case_bytes']) - int(a['worst_case_bytes'])) / MB:+.2f} MB"
        out.append(f"| {n} | {int(r['apple_download_bytes']) / MB:.2f} MB | {da} | {int(r['apple_install_bytes']) / MB:.2f} MB | "
                   f"{int(r['worst_case_bytes']) / MB:.2f} MB | {dw} | {int(r['payload_zip_bytes']) / MB:.2f} MB | "
                   f"{int(r['encrypted_bytes']) / MB:.2f} MB | {reproduce(rows, arm, 'apple_download_bytes')} |")
    for key in ("apple_download_bytes", "worst_case_bytes"):
        out += ["", f"RQ1 on {LABEL[key]}:", ""] + verdict_lines(rows, key)
    return "\n".join(out)


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("csv")
    p.add_argument("--md")
    a = p.parse_args()
    text = report(list(csv.DictReader(open(a.csv))))
    print(text)
    if a.md:
        open(a.md, "w").write(text + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
