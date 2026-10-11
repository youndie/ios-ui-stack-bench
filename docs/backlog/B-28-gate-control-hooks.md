---
id: B-28
title: "The positive controls RQ0 needs: a known launch delay, a known dirty allocation, a known resource"
status: wip
priority: P1
size: S
stage: stage-0-gate
blocked_by: [B-14]
---

# B-28 — Hooks for RQ0's positive controls

[B-06](B-06-rq0-the-gate.md) gives every metric a positive control: a 200 ms delay before "list
populated" must come out as +200 ms; a 50 MB allocation, written so the pages are dirty, must raise
`phys_footprint` by about that much; a 1 MB incompressible resource must raise the size proxy by
about 1 MB (that one is B-26's). The 50 ms stall exists since B-05. The other two need hooks in the
apps, built and checked before the devices arrive.

- **The decision and its reason.** Launch arguments of the shared instrumentation, absent from every
  measured run: `-benchDelayListMs <n>` holds the main thread for n ms just before the first row is
  reported, and `-benchAllocateMB <n>` allocates n MB at launch and touches every page. The same code
  in every arm, like the stall injector.
- Their own check, on the simulator: the reader sees the delay in `launch_to_list_ms` and the
  allocation in `peak_footprint_bytes`, against a run without the arguments. The numbers stay out of
  the repository; the check is that the effect appears, at about its size.

- AC: both hooks in `apps/common/Instrumentation/Bench.swift`, documented in its header, inert without
  their arguments.
- AC: on the simulator, with each argument, every arm's reader output moves in the expected
  direction by about the expected amount, against a run without it.
- Anchors: `apps/common/Instrumentation/Bench.swift`, `analysis/inapp_reader.py`.
