---
id: B-15
title: "The analysis: median and IQR per variant, bootstrap 95 % CIs, the verdict word per RQ"
status: wip
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
