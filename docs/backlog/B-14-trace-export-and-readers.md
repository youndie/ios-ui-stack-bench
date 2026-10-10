---
id: B-14
title: "xctrace record and export, and the readers that turn traces and in-app logs into CSVs"
status: done
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

---

## Findings — 2026-10-11

**Done for the in-app half; the Instruments half is split into [B-24](B-24-xctrace-record-and-readers.md).**
On the simulator, Animation Hitches records nothing and an App Launch recording hangs (research
§1.12). Readers for their tables cannot be written honestly until a device has produced an export to
write them against. B-16 now waits for B-24 too.

- **The reader** is `analysis/inapp_reader.py`. It turns one launch's log into `marks.csv`,
  `frames.csv`, `footprint.csv`, `scroll.csv`, `stalls.csv` and a one-row `summary.csv`. The summary
  holds:
  - validity, with its reason;
  - process start to first frame and to list populated;
  - peak footprint;
  - the scroll windows and frames in them;
  - the logger's hitch time ratio and longest hitch;
  - frame-interval p50 / p95 / p99;
  - the share of frames over budget.
- **Validity is the reader's, as B-13 left it.** A run counts only if its markers say the scenario
  happened as specified:
  - every run has `launch` → `firstFrame` → `listPopulated` once, in order;
  - S2: 40 alternating scroll pairs;
  - S3: 24 queries;
  - S4: 50 alternating detail pairs.

  Otherwise `valid=0`, with the reason, and the run is not repaired.
- **The logger's hitch accounting is defined in the reader's header before any number exists**
  (research §2, I4).
  - A hitch is a callback interval longer than 1.5 × the frame duration, which means a vsync was
    missed.
  - Hitch time is the interval minus that duration, summed inside S2's scroll windows, per second
    of window: ms/s, Apple's unit. The longest hitch is the largest single hitch time.
  - It measures main-thread callback cadence, so it is secondary to Instruments.
- **Its control** is `analysis/inapp_reader_control.py`, in `make check`. It runs 13 cases built in
  memory, with answers worked out by hand: clean 60 Hz, one 50 ms frame (33.33 ms of hitch over 40 s
  = 0.833 ms/s), jitter that is not a hitch, a stall outside the windows, a missed vsync at 120 Hz,
  startup intervals, and every kind of incomplete run.
  - **Shown failing:** a 1.0× hitch threshold fails the jitter case, and a removed S2 check fails the
    39-fling case.
- **On real simulator logs** (the 20-run matrix of B-13), all runs read valid except one. That run
  was C's S4: two push/pop cycles had been appended a quarter of an hour after the test passed, while
  the app stayed alive in the background. A clean rerun read valid. **The fix is in the harness:**
  every scenario now terminates the arm in `tearDown`.
- **`harness/collect.sh <arm> <scenario> <dir>`** runs a scenario, pulls the one log of that launch
  and reads it. On the simulator it refuses to write under `logs/`. With `-benchStallMs 50` on C, the
  logger registered the stalls and the run read valid. No simulator number is recorded here.
- **Not covered here:** `xctrace` recording and export, trace digests, and the device log pull. All
  of that is B-24.
