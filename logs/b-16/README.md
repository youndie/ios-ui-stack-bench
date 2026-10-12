# B-16 — the dry run on the iPhone XS, iteration 1

Recorded by `harness/dryrun.py`, read by `analysis/dryrun_reader.py` into `report.md`
(`python3 analysis/dryrun_reader.py logs/b-16 --md logs/b-16/report.md`).

- `ruler/` — a whole session of arm A alone, 2026-10-12, from commit `b30c6be` (`header.json`,
  `ruler-plan.json`): S1 by App Launch, S2–S4 through the harness. Its `runs.csv` is what the ruler
  reads.
- `runner/` — arm A idle, 5 launches with the UI-test runner and 5 without, interleaved. Recorded
  from commit `fec0496`, after the first attempt ran no test (the device's runner predated
  `testIdle`, and its empty runs are not kept). That run's header was overwritten by the next
  part's, so the commit is named here.
- `runner-c-kmp-cmp/` — the same for arm C, from commit `f77c56b` (`header-runner-c-kmp-cmp.json`).
- `instruments/` — A's launch (App Launch) and self-scrolling run (Animation Hitches) with the
  app's frame logger and footprint sampler on and off (`-benchInstrumentsOff 1`), from commit
  `b30c6be`. The self-scroll was then the 0 ↔ item 20 pattern; A2.2 replaced it.

What this iteration decided is BRIEF.md's late amendment A2.2. Memory, CPU and smoothness move to
launches with no runner, because the runner contaminates the app's own memory and CPU (kill
criterion 5) and the frame logger cannot see the render server. The ruler of this iteration
measures the metrics as they were read before A2.2. B-16's second iteration reruns it on A2.2's
metrics.
