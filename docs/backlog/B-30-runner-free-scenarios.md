---
id: B-30
title: "S2′ and S4′ without the runner: the app drives itself, the session records it (A2.2)"
status: open
priority: P0
size: M
stage: stage-2-harness
blocked_by: []
---

# B-30 — The runner-free scenarios of A2.2

Late amendment A2.2 moves memory, CPU and smoothness to launches that `xctrace --launch` starts, with
no UI-test runner attached: B-16 found the runner contaminating the app's own memory and CPU (kill
criterion 5) and the frame logger blind to the render server.

- **The decision and its reason.** The app drives itself, by launch arguments that are absent from
  every other run, in the same way in every arm:
  - S2′: `-benchAutoScroll 40`, the list scrolling a screen further 20 times and back
    (`Bench.autoScrollTarget`), recorded by Animation Hitches with Points of Interest;
  - S4′: `-benchAutoNavigate 50`, the first item's detail screen pushed and popped 50 times, one step
    a second, recorded by Activity Monitor as the memory cross-check.
  The app's own log of the same launch gives the footprint, the growth from cycle 5 to cycle 50
  (I7), and the CPU time.
- `harness/session.py` runs S1, S2′, S2 (harness, the logger's cross-check), S3 and S4′. The brief's
  counts apply, with S2′ and S4′ in place of S2 and S4 (10 runs each). `analysis/verdicts.py` reads
  RQ3 and RQ5's smoothness from the S2′ trace, and RQ4 and RQ5's memory from the S2′ and S4′ app
  logs.
- Not covered: whether S2′ resembles a finger's fling. It does not, and A2.2 says so.

- AC: `-benchAutoNavigate` in both stacks, its markers (`detailAppeared` / `detailDisappeared`)
  identical to S4's, checked on the simulator for every arm.
- AC: a session of two arms on the XS through the new path, every run valid. A session of one arm
  is B-16's ruler.
- AC: `analysis/verdicts.py` and its control read the new columns; `analysis/inapp_reader.py` reads
  S2′ and S4′ (their validity: 40 `autoScroll` steps; 50 alternating detail markers).
- Anchors: `harness/session.py`, `analysis/verdicts.py`, `apps/common/ListUI/Views.swift`,
  `compose-ui/src/commonMain/kotlin/bench/compose/App.kt`.
