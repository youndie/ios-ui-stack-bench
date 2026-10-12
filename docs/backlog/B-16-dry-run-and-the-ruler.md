---
id: B-16
title: "Dry run on one device: the ruler, the runner's and the instruments' own cost, thermal drift"
status: wip
priority: P1
size: M
stage: stage-2-harness
blocked_by: [B-15, B-24, B-30]
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

---

## Iteration 1 — 2026-10-12

Recorded on the XS into [logs/b-16/](../../logs/b-16/README.md), read into `report.md`.

- **The ruler, on the metrics as they were read before A2.2.** A against A comes out green on every
  component: startup (RQ2, RQ5), footprint (RQ4 ratio, RQ5 difference), and the logger's hitch time
  ratio (RQ5). The thermal state stayed nominal through all 50 attempts.
- **Kill criterion 5 fires.** With the runner attached, A's idle CPU time rises by 66 % and its
  footprint by 6.0 MB. C's rise by 55 % and 12.6 MB. That is far over the 10 % line, and not the same
  in every stack.
- **The logger reads zero hitch time for A in S2.** Animation Hitches reads A's self-scrolling launch
  well above zero. The logger sees main-thread stalls only (B-06 showed it sees those).
- **The instruments themselves** do not move A's launch, which stays inside the ruler with them on
  and off.

**What it decided.** These findings are late amendment A2.2, made by the owner. Memory, CPU and
smoothness move to launches with no runner, where the app drives itself: S2′ scrolls the list, S4′
navigates. Animation Hitches on S2′ is the smoothness instrument, and the logger on S2 is its
cross-check. The self-scroll became a screen per step, down and back up. On S2′ the XS drops frames
in A itself, about one a second, so RQ3's absolute bars are read beside A's own level.

**Bugs found and fixed on the way:**
- A run with no app log stopped the session as "battery None". It is now repeated, and the test's
  output is kept per attempt.
- A device runner older than its test sources ran nothing and reported success. `run.sh` now
  rebuilds when the sources are newer, and an empty run fails.

**Next.** [B-30](B-30-runner-free-scenarios.md) builds S2′ and S4′ into the session. Then this item
reruns the ruler on A2.2's metrics, and closes.
