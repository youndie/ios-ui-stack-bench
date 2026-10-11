---
id: B-28
title: "The positive controls RQ0 needs: a known launch delay, a known dirty allocation, a known resource"
status: done
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

---

## Findings — 2026-10-11

**Done on the simulator**; RQ0 ([B-06](B-06-rq0-the-gate.md)) uses both on the devices.

- **`-benchDelayListMs <n>`** holds the main thread for n ms when the first row appears, once, and
  logs a `control` line. **`-benchAllocateMB <n>`** allocates n MiB at launch, writes one byte in
  every 4 KiB page so all of it is dirty, holds it, and logs a `control` line. Both live in
  `Bench.swift`, are the same code in every arm, and do nothing without their argument.
- **The allocation** moved every arm's peak `phys_footprint` by about 50 MiB in a single S1 run each.
- **The delay** moved launch-to-list by about 200 ms only once runs were repeated. On arm A, five
  interleaved S1 runs with the delay and five without differ by about +200 ms at the median, and the
  clean runs' range is under 200 ms. **A single pair of runs cannot show it on the simulator.**
  Launch-to-list there varies by a few hundred milliseconds from run to run, and two arms' single
  pairs came out outside the expected range. B-06 therefore reads this control on repeated runs, at
  the median, never on one.
- **Where the delay lands differs by stack, and that is expected.** In the SwiftUI arms the first
  row's `onAppear` fires before the first frame, so the delay precedes `firstFrame` and leaves no gap
  in the frame log. In C the first row is composed after frames have started, so the delay shows as
  one long frame interval just before `listPopulated`. Either way launch-to-list grows by the delay,
  and that is the quantity RQ2 reads.
- No simulator number is recorded here.
