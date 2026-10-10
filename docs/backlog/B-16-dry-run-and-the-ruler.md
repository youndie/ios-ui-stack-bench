---
id: B-16
title: "Dry run on one device: the ruler, the runner's and the instruments' own cost, thermal drift"
status: open
priority: P1
size: M
stage: stage-2-harness
blocked_by: [B-15]
---

# B-16 — Dry run, ruler, contamination

The brief's P2 ends with a dry run on one device. This item makes it earn the right to compare
variants: before A is set against C, A is set against itself.

- **The ruler.** A against A, interleaved as the real comparison will be, on every metric a verdict
  rests on — the within-variant spread that kill criterion 4 compares with the A–C gap. If the
  ruler is wider than a threshold it guards, that RQ cannot reach green on this stand, and that is
  known before P3 rather than after.
- **Kill criterion 5.** The UI-test runner's CPU and memory during an idle run, against 10 % of the
  smallest variant's value per metric — as the brief writes it. The definition of "overhead" (the
  runner's own figures, or the shift in the app's figures with the runner attached versus launched
  without it) is settled in B-01; the second is the one that measures contamination
  ([research §2](../research/research-architecture.md), I6).
- **The study's own instruments.** The frame logger and the footprint sampler on and off in A:
  if switching them on moves A's hitch ratio or launch time outside the ruler, the instrument is
  part of the subject.
- **Thermal drift.** `ProcessInfo.thermalState` per run, and the time-ordered series of A's runs:
  a trend that the rotation is supposed to cancel is shown, not assumed.

- AC: under `logs/b-16/`, the ruler per metric with its runs, the runner's overhead per metric
  against the 10 % line, the instruments-on/off comparison and the thermal series.
- AC: any metric that fails kill criterion 5 is marked "in-app only" or "dropped" in BRIEF.md
  before P3 starts.
- Anchors: `logs/b-16/`, `harness/` (target).
