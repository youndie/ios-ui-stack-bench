---
id: B-14
title: "xctrace record and export, and the readers that turn traces and in-app logs into CSVs"
status: open
priority: P1
size: M
stage: stage-2-harness
blocked_by: [B-13]
---

# B-14 — Recording, export, readers

The brief: raw `.trace` hashes, exported CSVs and analysis scripts committed; numbers regenerated
from those files, never typed. This item is the path from a device session to CSVs: `xctrace
record` per scenario with the template of the metric, `xctrace export` of the tables that matter
(App Launch intervals, hitches with their durations, allocations / VM summary, CPU), the in-app logs
pulled from the app container, and one reader per source that writes one CSV schema.

- **The decision and its reason.** Every reader has a control on known input that `make check`
  runs: a fixture trace export and a fixture in-app log whose answer is written down by hand. A
  reader that silently drops rows produces the same CSV shape as one that reads them all.
- The in-app frame logger's hitch accounting is defined here, in the units of Apple's hitch time
  ratio, so that if [B-06](B-06-rq0-the-gate.md) leaves C's Animation Hitches unusable, RQ3 has a
  computation that was written before any number ([research §2](../research/research-architecture.md), I4).
- Not covered: statistics — [B-15](B-15-analysis-and-intervals.md).

- AC: one command per session produces the CSVs and the `.trace` hashes under `logs/b-NN/`.
- AC: each reader's control is in `make check` under `gate` and fails when the reader is broken
  (shown once by breaking it).
- AC: a reader reports rows it could not attribute instead of folding them away.
- Anchors: `harness/`, `analysis/` (target), `Makefile`.
