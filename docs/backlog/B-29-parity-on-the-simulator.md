---
id: B-29
title: "Bring the five arms to parity on the simulator, so B-11 on the devices confirms rather than builds"
status: done
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

---

## Findings — 2026-10-11

**Done on the simulator.** `harness/parity.sh` now reports the same geometry for all five arms within
one point:
- the number of visible rows;
- the first row's height and top;
- the last visible row's bottom;
- the thumbnail size, now read from the tree in C as well.

The numbers stay in `build/`. B-11 confirms this on the devices and fixes the pixel tolerance.

What C needed, each listed in `docs/flags.md` with its reason, and none of it leaving Material's
components:
- **Row text at iOS's text-style sizes in points**, at the font's natural line height, 2 dp apart
  like the SwiftUI `VStack`. Material's type scale had made C's row 12 points shorter.
- **The separator inside the row**, inset to the text as a SwiftUI separator is. As a separate 1 dp
  element it made the row pitch one point longer than the row, and C showed one row fewer.
- **The title at the large-title size, and the list running under the home indicator**, so C's list
  starts and ends where the SwiftUI list does. The search field stays at the top in C and sits in
  Liquid Glass at the bottom in A and B: chrome, outside the compared band (A1.4, I12).
- **A content description on the thumbnail**, so its 48 × 48 is read, not assumed.

C's S3 and S4 still pass with the reworked row. The B arms needed nothing: they draw A's views.
