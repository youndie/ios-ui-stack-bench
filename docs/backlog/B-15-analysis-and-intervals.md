---
id: B-15
title: "The analysis: median and IQR per variant, bootstrap 95 % CIs, the verdict word per RQ"
status: done
priority: P1
size: M
stage: stage-2-harness
blocked_by: [B-14]
---

# B-15 — Analysis

The brief: median and IQR per variant, a bootstrap 95 % CI for each A–B and A–C difference;
red/green decided on the median, and the CI must not cross the threshold. Written and tested on
synthetic data before any real CSV exists.

The rule as written fits the questions whose thresholds are differences (RQ2, RQ5) and not the
others: RQ3's thresholds are absolute values of C, RQ4's are a ratio to A and a growth within C,
RQ3's "no hitch ≥ 100 ms in any run" is a maximum, and RQ1 has no sample at all
([research §2](../research/research-architecture.md), I2). Which interval each one uses is an
amendment settled in [B-01](B-01-pins-and-the-amendment-window.md); this item implements what B-01
decided, and nothing else.

- **The decision and its reason.** The verdict is computed by the script from the thresholds as
  amended, and prints the verdict word — green, red, or inconclusive with the condition it missed —
  never a sign. Bootstrap with a fixed seed and the resample count printed, so a re-run gives the
  same interval.
- Positive control: synthetic arms with a known difference just outside, at, and inside a
  threshold must come out green, inconclusive and red as designed; arms drawn from one distribution
  must come out "below resolution".

- AC: the controls run in `make check` and fail when a threshold comparison is inverted (shown once).
- AC: the output table carries, per comparison, the estimator, the interval, the counted runs and a
  same-device, same-session line.
- Anchors: `analysis/` (target), `Makefile`.

---

## Findings — 2026-10-11

**Done.** `analysis/verdicts.py` turns the runs' summary rows (`runs.csv`) and the sizes
(`sizes.csv`) into one verdict per question. Each comparison it prints carries:
- the estimator, its value and its bootstrap 95 % interval;
- the counted runs per arm;
- a same-device-same-session line;
- the verdict word, with the condition a question missed.

The bootstrap is seeded (20261010) and does 10,000 resamples, so a re-run prints the same intervals.
Warm-up and invalid runs are not counted.

- **The brief's rule, applied to every component:** green or red is decided on the median, and the
  interval may not cross the threshold. Anything else is inconclusive and names what it missed. A
  question is green only if every component is, and red if any is. An arm with no counted runs is
  NOT MEASURED, never green.
- **What B-01 has to decide is implemented as a proposal, in one place** (`RULES` in the module's
  docstring and the `rq*` functions). BRIEF.md's amendments win wherever they differ:
  - **I2:** RQ3's absolute thresholds are held by the interval of C's median. The "no single hitch"
    conditions are a maximum over C's counted runs, with no interval. RQ4's ratio uses the interval
    of the ratio of medians. RQ1 is deterministic and compared as numbers.
  - **I3:** RQ4 and RQ5 are read on both devices and are green only if green on both. RQ2 stays on
    the older device, as the brief says.
  - **I7:** S4 growth runs from the sample after the 5th exit to the sample after the 50th. It is
    implemented in `analysis/inapp_reader.py`, with its own control case.
  - **I15** (new): "MB" is 10^6 bytes.
  - **A1.1:** RQ1's B − A and RQ5 are decided per B arm, with no best-of.
- **Which smoothness metric RQ3 and RQ5 read** is a parameter. Until B-24 has an Instruments reader it
  is the logger's hitch ratio (I4). After that it will be the Animation Hitches export, with the
  logger beside it.
- **Control:** `analysis/verdicts_control.py`, in `make check`, 15 cases.
  - Each RQ just inside, across and beyond its thresholds, plus an interval that crosses a threshold
    while the median does not.
  - The same-session line, NOT MEASURED, and counting.
  - The seeded bootstrap.
  - **Shown failing:** RQ2's `<= 100` inverted to `>= 100` fails three cases.
- **Changed from the item's text:** the item expected arms drawn from one distribution to come out
  "below resolution". In this engine they come out by the question's thresholds — green where the
  threshold is a difference that zero satisfies (RQ5 B1 against A, a case in the control) — because
  the brief's verdict words are green / red / inconclusive.
