#!/usr/bin/env python3
"""B-11's parity verdict from `harness/parity.sh`'s output, by BRIEF.md A1.6.

    python3 analysis/parity_reader.py <dir> [--csv parity.csv] [--md parity.md]

<dir> holds `<arm>.txt` (the `PARITY key=value` geometry, in points) and `<arm>.png` (the first
screen) for the five arms. A is the reference. **The rule, A1.6, fixed before the first diff on a
device:**

    geometry, every arm against A
        the same count of visible rows; the first row's height and top, the last visible row's
        bottom, and the thumbnail's width and height each within 1 point
    pixels, A against B1, B2 and B3
        at most 1 % of the band's pixels differ - the band from A's first row's top to its last
        visible row's bottom, full width, one channel differing by more than 32 of 255
        (scripts/parity_diff.py)
    pixels, A against C
        computed over the same band and published; it decides nothing (glyph rasterisation differs
        whatever the layout does)

A pair is `pass`, `fail` or `missing`; parity holds when every pair passes. Standard library only.
"""
import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import parity_diff  # noqa: E402

ARMS = ["a-native", "b1-objc", "b2-skie", "b3-swift-export", "c-kmp-cmp"]
B_ARMS = ("b1-objc", "b2-skie", "b3-swift-export")
POINT_TOLERANCE = 1.0
PIXEL_TOLERANCE = 0.01
DELTA = 32


def geometry(path):
    if not os.path.exists(path):
        return None
    g = {}
    for line in open(path):
        if "=" in line:
            k, v = line.strip().split("=", 1)
            g[k] = v
    return g


def thumb(g):
    try:
        w, h = g.get("thumb", "").split("x")
        return float(w), float(h)
    except ValueError:
        return None


def geometry_row(arm, a, x):
    if a is None or x is None:
        return {"arm": arm, "check": "geometry", "verdict": "missing", "observed": "no PARITY output"}
    misses = []
    if a.get("rows") != x.get("rows"):
        misses.append(f"rows {x.get('rows')} vs {a.get('rows')}")
    for key in ("row_height", "row_top", "list_bottom"):
        d = float(x[key]) - float(a[key])
        if abs(d) > POINT_TOLERANCE:
            misses.append(f"{key} {d:+.2f} pt")
    ta, tx = thumb(a), thumb(x)
    if ta is None or tx is None or any(abs(p - q) > POINT_TOLERANCE for p, q in zip(ta, tx)):
        misses.append(f"thumb {x.get('thumb')} vs {a.get('thumb')}")
    observed = (f"rows {x['rows']}, row_height {float(x['row_height']) - float(a['row_height']):+.2f}, "
                f"row_top {float(x['row_top']) - float(a['row_top']):+.2f}, "
                f"list_bottom {float(x['list_bottom']) - float(a['list_bottom']):+.2f} pt, thumb {x.get('thumb')}")
    return {"arm": arm, "check": "geometry", "verdict": "fail" if misses else "pass",
            "observed": "; ".join(misses) if misses else observed}


def pixel_row(arm, a, png_a, png_x):
    if a is None or not os.path.exists(png_a) or not os.path.exists(png_x):
        return {"arm": arm, "check": "pixels", "verdict": "missing", "observed": "no screenshot"}
    scale = float(a.get("scale", 3))
    pa, px = (parity_diff.decode(open(p, "rb").read()) for p in (png_a, png_x))
    share = parity_diff.differing_share(pa, px, int(float(a["row_top"]) * scale), int(float(a["list_bottom"]) * scale), DELTA)
    if arm in B_ARMS:
        verdict = "pass" if share <= PIXEL_TOLERANCE else "fail"
    else:
        verdict = "published"
    return {"arm": arm, "check": "pixels", "verdict": verdict, "observed": f"{100 * share:.3f} % of the band differ"}


def rows(d):
    a = geometry(os.path.join(d, "a-native.txt"))
    out = []
    for arm in ARMS[1:]:
        x = geometry(os.path.join(d, f"{arm}.txt"))
        out.append(geometry_row(arm, a, x))
        out.append(pixel_row(arm, a, os.path.join(d, "a-native.png"), os.path.join(d, f"{arm}.png")))
    return out


def verdict(table):
    decisive = [r for r in table if r["verdict"] != "published"]
    if any(r["verdict"] == "missing" for r in decisive):
        return "NOT CHECKED - " + "; ".join(f"{r['arm']} {r['check']}" for r in decisive if r["verdict"] == "missing")
    failed = [r for r in decisive if r["verdict"] == "fail"]
    return "PARITY" if not failed else "NO PARITY - " + "; ".join(f"{r['arm']} {r['check']}" for r in failed)


def markdown(table):
    out = [f"Parity against A: **{verdict(table)}**", "", "| Arm | Check | Observed | Verdict |", "|---|---|---|---|"]
    out += [f"| {r['arm']} | {r['check']} | {r['observed']} | {r['verdict']} |" for r in table]
    return "\n".join(out)


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("dir")
    p.add_argument("--csv")
    p.add_argument("--md")
    a = p.parse_args()
    table = rows(a.dir)
    text = markdown(table)
    print(text)
    if a.csv:
        with open(a.csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["arm", "check", "verdict", "observed"])
            w.writeheader()
            w.writerows(table)
    if a.md:
        open(a.md, "w").write(text + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
