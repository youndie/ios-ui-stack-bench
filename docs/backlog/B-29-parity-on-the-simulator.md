---
id: B-29
title: "Bring the five arms to parity on the simulator, so B-11 on the devices confirms rather than builds"
status: wip
priority: P1
size: M
stage: stage-1-build
blocked_by: [B-27]
---

# B-29 — Parity on the simulator, before the devices

The parity tooling of [B-27](B-27-parity-tooling.md), run on the simulator, shows the arms' first
screens do not yet agree in geometry: the SwiftUI arms and the Compose arm lay out their rows at
different heights, and the Compose tree does not expose the thumbnail as an image. B-11's check runs
on the devices, under a five-working-day budget (kill criterion 3), and the owner brings the devices
once the runs are ready — so the layout work belongs here, where it costs no device time.

- **The decision and its reason.** Match C's row to the SwiftUI row in points — paddings, text
  styles, thumbnail and badge size — without leaving either stack's idiomatic components: the target
  is "same row height in points, same item count, same thumbnail size" (A1.4, I12), not identical
  pixels, which Liquid Glass rules out anyway (research §1.7). Each value changed is listed in
  `docs/flags.md` if it departs from a component's default.
- Where geometry cannot match without leaving a stack's defaults, that is recorded and handed to
  B-11, not forced.
- Not covered: the tolerance number and the verdict — B-11's, on the devices.

- AC: `harness/parity.sh` on the simulator reports, for all five arms, the same number of visible
  rows and row heights equal within one point; the numbers stay out of the repository, the comparison
  in the pull request says equal or not.
- AC: the Compose thumbnail is exposed to the accessibility tree (a content description), so its size
  is read rather than assumed — the same in every arm.
- Anchors: `compose-ui/src/commonMain/kotlin/bench/compose/App.kt`, `apps/common/ListUI/Views.swift`,
  `docs/flags.md`.
