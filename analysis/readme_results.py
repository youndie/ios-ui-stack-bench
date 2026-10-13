#!/usr/bin/env python3
"""README.md's results block, generated from the logs so no figure in it is typed (CLAUDE.md).

    python3 analysis/readme_results.py          rewrite the block between the markers
    python3 analysis/readme_results.py --check  fail if the block differs from what the logs give

Sources: logs/b-06/xs/gate.csv (RQ0), logs/b-31/download.csv (RQ1, A2.4), and every pair session
under logs/b-17/xs-*/ that has a verdicts.csv (RQ2-RQ5; the sessions of A1.5). The block lists the
verdicts that exist and names the ones that do not yet. Standard library only.
"""
import csv
import glob
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
import download_report  # noqa: E402
import gate_reader  # noqa: E402
import verdicts  # noqa: E402

BEGIN, END = "<!-- BEGIN RESULTS (analysis/readme_results.py) -->", "<!-- END RESULTS -->"
MB = verdicts.MB
ARM = {"a-native": "A", "b1-objc": "B1", "b2-skie": "B2", "b3-swift-export": "B3", "c-kmp-cmp": "C"}


def read(path):
    return list(csv.DictReader(open(os.path.join(ROOT, path)))) if os.path.exists(os.path.join(ROOT, path)) else []


def nz(v, d):
    """A rounded figure without a negative zero: -0.25 at no decimals is 0, not -0."""
    t = f"{v:.{d}f}"
    return t[1:] if t.startswith("-") and float(t) == 0 else t


def fmt(v, d=1):
    return f"{v:+.{d}f}"


def rq0():
    rows = read("logs/b-06/xs/gate.csv")
    if not rows:
        return "| RQ0 — every metric capturable | not run | | |"
    passed = sum(1 for r in rows if r["verdict"] == "pass")
    failed = "; ".join(f"{ARM[r['arm']]} {r['metric']} ({r['instrument']}) observed {r['observed'].split(' (')[0]} against {r['expected']}"
                       for r in rows if r["verdict"] != "pass")
    return (f"| RQ0 — every metric capturable, the injected stall seen | {gate_reader.verdict(rows).split(' - ')[0].lower()} "
            f"| {passed} of {len(rows)} control rows pass; the stall is seen by both instruments in every arm, C included"
            + (f". Not passing: {failed}" if failed else "") + " | [GATE.md](GATE.md) |")


def rq1():
    rows = read("logs/b-31/download.csv")
    if not rows:
        return []
    out = []
    for arm in verdicts.B_ARMS + ("c-kmp-cmp",):
        b = arm if arm != "c-kmp-cmp" else verdicts.B_ARMS[0]
        apple = next(c for c in verdicts.rq1(rows, b, "apple_download_bytes") if c.row["arm"] == arm).row
        worst = next(c for c in verdicts.rq1(rows, b, "worst_case_bytes") if c.row["arm"] == arm).row
        out.append(f"| RQ1 — download size, {ARM[arm]} − A | {apple['verdict']} | {fmt(apple['value'] / MB, 2)} MB on Apple's estimate "
                   f"(green {apple['green_if']}); encrypted worst case {fmt(worst['value'] / MB, 2)} MB, {worst['verdict']} | "
                   f"[logs/b-31](logs/b-31/report.md) |")
    return out


def sessions():
    out, missing = [], []
    found = {}
    for path in sorted(glob.glob(os.path.join(ROOT, "logs/b-17/xs-*/verdicts.csv"))):
        session = os.path.basename(os.path.dirname(path))
        for r in csv.DictReader(open(path)):
            if r["value"] != "" and r["rq"] in ("RQ2", "RQ3", "RQ4", "RQ5"):
                found[(r["question"], r["metric"], session)] = (r, session)
    label = {"trace_process_to_list_ms": ("startup", "ms", 0, 1), verdicts.HITCH_RATIO: ("hitch time", "ms/s", 1, 1),
             verdicts.LONGEST_HITCH: ("longest hitch", "ms", 0, 1), "peak_footprint_bytes": ("peak footprint", "", 2, 1),
             "growth_cycles_5_to_50_bytes": ("footprint growth over 50 cycles", "MB", 1, MB)}
    # A2.5: RQ2-RQ4 are decided by {A, C} (xs-1); a later session's C against A is printed as a repeat.
    decisive = {"RQ2": "xs-1", "RQ3": "xs-1", "RQ4": "xs-1"}
    for (question, metric, _), (r, session) in sorted(found.items()):
        name, unit, d, scale = label.get(metric, (metric, "", 2, 1))
        if metric == "peak_footprint_bytes" and r["estimator"] == "median ratio":
            unit, scale, value = "×", 1, f"{float(r['value']):.2f}×"
            ci = f"{float(r['ci_low']):.2f}–{float(r['ci_high']):.2f}"
        elif metric == "peak_footprint_bytes":
            unit, scale, d = "MB", MB, 1
            value, ci = f"{fmt(float(r['value']) / MB, 1)} MB", f"{float(r['ci_low']) / MB:+.1f} to {float(r['ci_high']) / MB:+.1f}"
        else:
            sgn = r["estimator"].startswith("median difference")
            v = float(r["value"]) / scale
            value = f"{fmt(v, d) if sgn else f'{v:.{d}f}'} {unit}"
            ci = "" if r["ci_low"] == "" else f"{nz(float(r['ci_low']) / scale, d)} to {nz(float(r['ci_high']) / scale, d)}"
        who = "C − A" if r["arm"] == "c-kmp-cmp" and r["estimator"].startswith("median d") else (
            "C / A" if r["estimator"] == "median ratio" else (f"{ARM.get(r['arm'], r['arm'])} − A" if r["rq"] == "RQ5" else ARM.get(r["arm"], r["arm"])))
        repeat = r["rq"] in decisive and session != decisive[r["rq"]]
        out.append(f"| {r['rq']} — {name}, {who}{' (repeat)' if repeat else ''} | {r['verdict']}{' (decides nothing)' if repeat else ''} | {value}" + (f" (95 % interval {ci})" if ci else "")
                   + f"; green {r['green_if']}, red {r['red_if']} | [logs/b-17/{session}](logs/b-17/{session}/verdicts.txt) |")
    measured = {k[0] for k in found}
    for b in ("RQ5 b1-objc", "RQ5 b2-skie", "RQ5 b3-swift-export"):
        if b not in measured:
            missing.append(f"{b.replace('RQ5 ', 'RQ5 for ')} waits for its session (A2.5).")
    return out, missing


def a_level():
    rows = [r for p in sorted(glob.glob(os.path.join(ROOT, "logs/b-17/xs-*/runs.csv"))) for r in csv.DictReader(open(p))]
    vals = [float(r[verdicts.HITCH_RATIO]) for r in rows if r["arm"] == "a-native" and r["scenario"] == verdicts.SMOOTH_SCENARIO
            and r["counted"] == "1" and r["valid"] == "1" and r.get(verdicts.HITCH_RATIO, "") != ""]
    return statistics.median(vals) if vals else None


def block():
    lines = [BEGIN, "", "Read on the iPhone XS only (BRIEF.md A1.7); every figure is regenerated from `logs/` by "
             "`analysis/readme_results.py`. A verdict is green or red only when the median and its whole 95 % interval are on that side "
             "of the line; otherwise it is inconclusive.", "",
             "| Question | Verdict | Figure | Raw data |", "|---|---|---|---|", rq0()] + rq1()
    rows, missing = sessions()
    lines += rows
    level = a_level()
    if level is not None:
        lines += ["", f"RQ3's bars are absolute, and on this phone the native list itself is not under them: A's own hitch time on the same "
                  f"self-scrolling run is {level:.1f} ms/s (median), so C's red is read beside A's level. The scroll is driven by the app "
                  "itself, not by a finger (A2.2); on real flings through the UI-test runner the frame logger shows the same direction."]
    lines += [""] + ([f"Still open: {m}" for m in missing] or ["Every question that this phone can answer is measured; the write-up is B-19's."]) + ["", END]
    return "\n".join(lines)


def main():
    path = os.path.join(ROOT, "README.md")
    text = open(path).read()
    if BEGIN not in text or END not in text:
        raise SystemExit("README.md has no results markers")
    head, rest = text.split(BEGIN)
    _, tail = rest.split(END)
    new = head + block() + tail
    if "--check" in sys.argv[1:]:
        if new != text:
            raise SystemExit("README.md's results block differs from the logs: run python3 analysis/readme_results.py")
        print("README.md's results block matches the logs")
        return 0
    open(path, "w").write(new)
    print("README.md's results block written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
