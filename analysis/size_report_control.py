#!/usr/bin/env python3
"""The control for analysis/size_report.py: sizes.csv rows whose report is known (B-12).

    python3 analysis/size_report_control.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import size_report as sr  # noqa: E402

MAPS = {f"map_{k}": "0" for k in sr.MAP}


def row(arm, build, zipped, exe=1000, sha="x", det="1"):
    return {"arm": arm, "build": str(build), "uncompressed_bytes": "5000", "compressed_bytes": str(zipped), "executable_bytes": str(exe),
            "executable_sha256": sha, "control_1mib_delta": str(1 << 20), "deterministic": det, **MAPS}


def rows(b2_second=1_000_000 + 3_000_000):
    out = []
    for arm, z in (("a-native", 1_000_000), ("b1-objc", 3_000_000), ("b2-skie", 4_000_000), ("b3-swift-export", 6_000_001), ("c-kmp-cmp", 13_000_000)):
        out += [row(arm, 1, z, det="0" if arm == "b2-skie" else "1"), row(arm, 2, b2_second if arm == "b2-skie" else z, det="0" if arm == "b2-skie" else "1")]
    return out


CASES = [
    ("B1 +2.00 MB is green (the bar is inclusive), B2 +3.00 MB inconclusive, B3 +5.000001 MB red, C +12.00 MB green",
     lambda t: "b1-objc - a-native = +2.00 MB**: green" in t and "b2-skie - a-native = +3.00 MB**: inconclusive" in t
     and "b3-swift-export - a-native = +5.00 MB**: red" in t and "c-kmp-cmp - a-native = +12.00 MB**: green" in t),
    ("a second build whose zip differs by bytes at the same executable size says so",
     lambda t: "differ in bytes, same size; zip +0 bytes" in t),
    ("the 1 MiB control is printed in MiB", lambda t: "+1.000 MiB" in t),
]


def main():
    text = sr.report(rows())
    failed = 0
    for name, check in CASES:
        ok = bool(check(text))
        failed += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    print(f"control for size_report.py: {len(CASES) - failed}/{len(CASES)} cases behave")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
