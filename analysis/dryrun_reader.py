#!/usr/bin/env python3
"""B-16's report from harness/dryrun.py's output: the ruler, the runner's contamination, the instruments.

    python3 analysis/dryrun_reader.py <dir> [--md report.md]

**The ruler.** A's counted, valid runs of the ruler session are split into two interleaved halves:
run indices 1, 3, 5, ... and 2, 4, 6, ... (run 0 is the warm-up). The halves are then fed to
analysis/verdicts.py as if they were two arms: the even half as A, the odd half as C for RQ2 and
RQ4, and as B1 for RQ5. A against itself, read by the study's own rules, must come out GREEN. A
component that does not shows that its threshold is narrower than the stand can resolve, and the RQ
cannot reach green on this stand. That is known before the sessions (kill criterion 4's spread).
RQ3 holds C to absolute bars, so its ruler is A's own interval, printed beside the bar.

**Kill criterion 5** (I6): the app's own figures in an idle launch - the list, then 30 s untouched -
launched by the UI-test runner and by `devicectl` with no runner, 5 of each, interleaved. The shift
is the median with the runner minus the median without, per metric: CPU time (`cpu_total_ms`) and
peak footprint. It passes when it is within 10 % of the value without the runner. A's value stands
for "the smallest variant's" (the brief), because A is the smallest arm on both metrics in every
recording so far.

**The study's own instruments**: the frame logger and the footprint sampler off (`-benchInstrumentsOff
1`) against on. The figures are startup from App Launch (5 + 5) and the hitch time ratio from Animation
Hitches on the self-scrolling run (3 + 3), reported as the median on minus the median off. A startup
shift is judged against the ruler's startup interval: outside it, the instrument is part of the
subject.

**Thermal drift**: the worst thermal state of each ruler run, in time order, and the count of runs
repeated for it. Standard library only.
"""
import argparse
import csv
import glob
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inapp_reader  # noqa: E402
import verdicts  # noqa: E402
import xctrace_reader  # noqa: E402

MB = verdicts.MB


def ruler_rows(runs):
    """The ruler session's rows, its A runs relabelled into two halves."""
    out = []
    for r in runs:
        if r["arm"] != "a-native":
            continue
        run = int(r["run"])
        half = None if run == 0 else ("a-native" if run % 2 == 0 else "x")
        if half:
            out.append({**r, "arm": half, "device": "older"})
    return out


def as_arm(rows, name):
    return [{**r, "arm": name if r["arm"] == "x" else r["arm"]} for r in rows]


def ruler(runs):
    rows = ruler_rows(runs)
    out = []
    for name, comps in (("RQ2 (A vs A as C)", verdicts.rq2(as_arm(rows, "c-kmp-cmp"))),
                        ("RQ4 (A vs A as C)", [c for c in verdicts.rq4(as_arm(rows, "c-kmp-cmp")) if c.row["estimator"] != "median"]),
                        ("RQ5 (A vs A as B1)", verdicts.rq5(as_arm(rows, "b1-objc"), "b1-objc"))):
        for c in comps:
            r = c.row
            out.append({"question": name, "metric": r["metric"], "estimator": r["estimator"], "value": r["value"],
                        "ci_low": r["ci_low"], "ci_high": r["ci_high"], "runs": r["runs"], "verdict": r["verdict"],
                        "green_if": r["green_if"]})
    # RQ3's bars are absolute: A's own median and interval, beside them.
    for metric in (verdicts.HITCH_RATIO,):
        both = verdicts.counted([{**r, "arm": "a"} for r in rows], "a", "older", verdicts.SMOOTH_SCENARIO, metric)
        if len(both) >= 2:
            lo, hi = verdicts.bootstrap(statistics.median, [both])
            out.append({"question": "RQ3 (A's own level)", "metric": metric, "estimator": "median", "value": statistics.median(both),
                        "ci_low": lo, "ci_high": hi, "runs": str(len(both)), "verdict": "reference", "green_if": "< 5 ms/s for C"})
    return out


def app_figures(run_dir):
    path = os.path.join(run_dir, "app.ndjson")
    if not os.path.exists(path):
        return None
    lines = inapp_reader.load(path)
    foot = [l for l in lines if l["k"] == "footprint"]
    cpu = [l["cpuMs"] for l in foot if l.get("cpuMs", -1) >= 0]
    return {"cpu_total_ms": max(cpu) if cpu else None, "peak_footprint_bytes": max((l["bytes"] for l in foot), default=None)}


def runner(d):
    out = []
    for metric, unit, scale in (("cpu_total_ms", "ms", 1), ("peak_footprint_bytes", "MB", MB)):
        with_ = [f[metric] for f in (app_figures(p) for p in sorted(glob.glob(os.path.join(d, "runner", "with-*")))) if f and f[metric] is not None]
        without = [f[metric] for f in (app_figures(p) for p in sorted(glob.glob(os.path.join(d, "runner", "without-*")))) if f and f[metric] is not None]
        if not with_ or not without:
            out.append({"metric": metric, "verdict": "not measured", "runs": f"{len(with_)}/{len(without)}"})
            continue
        shift = statistics.median(with_) - statistics.median(without)
        line = 0.10 * statistics.median(without)
        out.append({"metric": metric, "with": statistics.median(with_) / scale, "without": statistics.median(without) / scale,
                    "shift": shift / scale, "line": line / scale, "unit": unit, "runs": f"{len(with_)}/{len(without)}",
                    "verdict": "pass" if abs(shift) <= line else "fail - kill criterion 5"})
    return out


def instruments(d, startup_ci):
    out = []
    for kind, fn, key, unit in (("launch", xctrace_reader.launch, "trace_process_to_list_ms", "ms"),
                                ("hitches", xctrace_reader.hitch_summary, "trace_hitch_time_ratio_ms_per_s", "ms/s")):
        on = [fn(p)[key] for p in sorted(glob.glob(os.path.join(d, "instruments", f"{kind}-on-*")))]
        off = [fn(p)[key] for p in sorted(glob.glob(os.path.join(d, "instruments", f"{kind}-off-*")))]
        on, off = [x for x in on if x != ""], [x for x in off if x != ""]
        if not on or not off:
            out.append({"metric": key, "verdict": "not measured", "runs": f"{len(on)}/{len(off)}"})
            continue
        shift = statistics.median(on) - statistics.median(off)
        if kind == "launch" and startup_ci:
            verdict = "inside the ruler" if startup_ci[0] <= shift <= startup_ci[1] else "outside the ruler - the instruments are part of the subject"
        else:
            verdict = "reported"
        out.append({"metric": key, "on": statistics.median(on), "off": statistics.median(off), "shift": shift, "unit": unit,
                    "runs": f"{len(on)}/{len(off)}", "verdict": verdict})
    return out


def thermal(runs):
    rows = sorted((r for r in runs if r["arm"] == "a-native"), key=lambda r: (verdicts_order(r)))
    states = [r.get("thermal_worst", "") for r in rows]
    repeated = sum(1 for r in rows if r.get("decision") == "repeat" and "thermal" in r.get("why", ""))
    return states, repeated


def verdicts_order(r):
    order = ["S1", "S2p", "S2", "S3", "S4p", "S4"]
    return (order.index(r["scenario"]) if r["scenario"] in order else len(order), int(r["run"]), int(r["attempt"]))


def fmt(x, unit=""):
    return "" if x in ("", None) else f"{x:.2f}{(' ' + unit) if unit else ''}"


def report(d):
    runs_path = os.path.join(d, "ruler", "runs.csv")
    runs = list(csv.DictReader(open(runs_path))) if os.path.exists(runs_path) else []
    rul = ruler(runs) if runs else []
    startup = next((r for r in rul if r["question"].startswith("RQ2")), None)
    startup_ci = (startup["ci_low"], startup["ci_high"]) if startup and startup["ci_low"] != "" else None
    lines = ["## The ruler: A against A, by the study's own rules", "",
             "| Question | Metric | Estimator | A' - A | 95 % interval | Runs | Verdict | Green if |", "|---|---|---|---|---|---|---|---|"]
    for r in rul:
        lines.append(f"| {r['question']} | {r['metric']} | {r['estimator']} | {fmt(r['value'])} | ({fmt(r['ci_low'])}, {fmt(r['ci_high'])}) | {r['runs']} | {r['verdict']} | {r['green_if']} |")
    if not rul:
        lines.append("| not measured | | | | | | | |")
    lines += ["", "## Kill criterion 5: the app's own figures, idle, with the runner and without", "",
              "| Metric | With | Without | Shift | 10 % line | Runs | Verdict |", "|---|---|---|---|---|---|---|"]
    for r in runner(d):
        lines.append(f"| {r['metric']} | {fmt(r.get('with'), r.get('unit', ''))} | {fmt(r.get('without'), r.get('unit', ''))} | "
                     f"{fmt(r.get('shift'), r.get('unit', ''))} | {fmt(r.get('line'), r.get('unit', ''))} | {r['runs']} | {r['verdict']} |")
    lines += ["", "## The study's own instruments: on minus off", "",
              "| Metric | On | Off | Shift | Runs | Verdict |", "|---|---|---|---|---|---|"]
    for r in instruments(d, startup_ci):
        lines.append(f"| {r['metric']} | {fmt(r.get('on'))} | {fmt(r.get('off'))} | {fmt(r.get('shift'), r.get('unit', ''))} | {r['runs']} | {r['verdict']} |")
    states, repeated = thermal(runs)
    lines += ["", "## Thermal drift", "",
              f"The worst thermal state of every ruler attempt, in the session's order: {', '.join(states) if states else 'not measured'}. "
              f"Attempts repeated for a thermal state above nominal: {repeated}."]
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("dir")
    p.add_argument("--md")
    a = p.parse_args()
    text = report(a.dir)
    print(text)
    if a.md:
        open(a.md, "w").write(text + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
