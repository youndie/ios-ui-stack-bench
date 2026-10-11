#!/usr/bin/env python3
"""The control for analysis/parity_reader.py: synthetic first screens whose verdict is known.

    python3 analysis/parity_reader_control.py

Each case writes five arms' `PARITY` geometry and 30 x 100-pixel screenshots (scale 1, so points are
pixels) into a temporary directory. The band is rows 20-80. Pixels outside it may differ freely.
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "scripts"))
import parity_reader as pr  # noqa: E402
from parity_diff_control import encode  # noqa: E402

W, H = 30, 100
BASE = {"rows": "9", "row_height": "76.67", "row_top": "20", "list_bottom": "80", "thumb": "48.0x48.0", "scale": "1"}


def screen(changed_rows=()):
    return encode(W, H, lambda x, y: (200, 0, 0) if y in changed_rows else (10, 20, 30))


def build(d, geometry=None, pngs=None, skip=()):
    for arm in pr.ARMS:
        if arm in skip:
            continue
        g = {**BASE, **(geometry or {}).get(arm, {})}
        open(os.path.join(d, f"{arm}.txt"), "w").write("".join(f"{k}={v}\n" for k, v in g.items()))
        open(os.path.join(d, f"{arm}.png"), "wb").write((pngs or {}).get(arm, screen()))
    return pr.rows(d)


def find(table, arm, check):
    return next(r for r in table if r["arm"] == arm and r["check"] == check)


CASES = []


def case(name):
    def register(fn):
        CASES.append((name, fn))
        return fn
    return register


@case("identical arms: parity; C's pixel share is published, not judged")
def _(d):
    t = build(d)
    return pr.verdict(t) == "PARITY" and find(t, "c-kmp-cmp", "pixels")["verdict"] == "published"


@case("C's first row 0.9 pt lower passes; 1.5 pt lower fails")
def _(d):
    ok = pr.verdict(build(d, {"c-kmp-cmp": {"row_top": "20.9"}})) == "PARITY"
    return ok and pr.verdict(build(d, {"c-kmp-cmp": {"row_top": "21.5"}})).startswith("NO PARITY - c-kmp-cmp geometry")


@case("one row fewer fails, whatever the points say")
def _(d):
    return pr.verdict(build(d, {"b2-skie": {"rows": "8"}})).startswith("NO PARITY - b2-skie geometry")


@case("B1 differing in 1 of 60 band rows (1.7 %) fails; C differing as much is only published")
def _(d):
    t = build(d, pngs={"b1-objc": screen({50}), "c-kmp-cmp": screen({50})})
    return find(t, "b1-objc", "pixels")["verdict"] == "fail" and find(t, "c-kmp-cmp", "pixels")["verdict"] == "published" \
        and pr.verdict(t) == "NO PARITY - b1-objc pixels"


@case("differences outside the band do not count")
def _(d):
    return pr.verdict(build(d, pngs={"b3-swift-export": screen(set(range(0, 20)) | set(range(81, 100)))})) == "PARITY"


@case("a thumbnail the tree does not expose fails geometry")
def _(d):
    return pr.verdict(build(d, {"c-kmp-cmp": {"thumb": "not exposed"}})).startswith("NO PARITY - c-kmp-cmp geometry")


@case("an arm without output is NOT CHECKED, never parity")
def _(d):
    return pr.verdict(build(d, skip=("b3-swift-export",))).startswith("NOT CHECKED")


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
    print(f"control for parity_reader.py: {len(CASES) - failed}/{len(CASES)} cases behave")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
