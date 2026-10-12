#!/usr/bin/env python3
"""The control for analysis/download_report.py: download.csv rows whose report is known (B-31).

    python3 analysis/download_report_control.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import download_report as dr  # noqa: E402


def row(arm, build, apple, worst):
    return {"arm": arm, "build": str(build), "apple_download_bytes": str(apple), "apple_install_bytes": str(3 * apple),
            "payload_zip_bytes": str(apple - 1000), "worst_case_bytes": str(worst), "encrypted_bytes": "100000",
            "executable_sha256": "x", "variant": "v.ipa"}


ROWS = []
for arm, apple, worst in (("a-native", 1_000_000, 1_100_000), ("b1-objc", 2_500_000, 4_200_000), ("b2-skie", 3_000_000, 6_200_000),
                          ("b3-swift-export", 2_900_000, 3_000_000), ("c-kmp-cmp", 11_000_000, 30_000_000)):
    ROWS += [row(arm, 1, apple, worst), row(arm, 2, apple + (7 if arm == "c-kmp-cmp" else 0), worst)]

CASES = [
    ("Apple's estimate decides: B1 +1.50 MB green, B2 +2.00 MB green (inclusive), C +10.00 MB green",
     lambda t: t.split("encrypted worst case")[0].count("green") >= 4 and "b2-skie - a-native = **+2.00 MB**: green" in t),
    ("the worst case is printed with its own verdicts: B2 +5.10 MB red, B1 +3.10 inconclusive, C +28.90 MB red",
     lambda t: "b2-skie - a-native = **+5.10 MB**: red" in t.split("encrypted worst case")[1]
     and "b1-objc - a-native = **+3.10 MB**: inconclusive" in t.split("encrypted worst case")[1]
     and "c-kmp-cmp - a-native = **+28.90 MB**: red" in t.split("encrypted worst case")[1]),
    ("a second build 7 bytes larger is reported as such; equal builds as identical",
     lambda t: "+7 bytes" in t and "identical" in t),
]


def main():
    text = dr.report(ROWS)
    failed = 0
    for name, check in CASES:
        ok = bool(check(text))
        failed += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    print(f"control for download_report.py: {len(CASES) - failed}/{len(CASES)} cases behave")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
