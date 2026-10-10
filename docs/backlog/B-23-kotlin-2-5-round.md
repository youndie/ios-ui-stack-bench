---
id: B-23
title: "A later round on Kotlin 2.5.0: arm B3 without D8, once Kotlin 2.5.0 is stable"
status: open
priority: P3
size: M
stage: stage-5-later
---

# B-23 — A later round on Kotlin 2.5.0: B3 without D8

D8 keeps kotlinx-serialization internal to the shared module, because Swift export on every stable
Kotlin cannot compile its API (KT-87791, research §1.11). The owner kept D8 for this study
(2026-10-10) and asked for B3 to be tried again on **Kotlin 2.5.0**, where the fix is
("available in 2.5.0-Beta1"), with the shared module as it would idiomatically be written:
`@Serializable` on the public `Item`.

- **The decision and its reason.** This is a separate round, not a change of the study's pin.
  SKIE 0.10.15 refuses every Kotlin after 2.4.20 (research §1.11), so on 2.5.0 arm B2 cannot be built,
  and one Kotlin for every arm is what keeps the shared module the same bytes. The round therefore
  compares B3 on 2.5.0 with A, and with B1 and C rebuilt on 2.5.0. It is not set beside the main study's
  B2.
- **When.** Not before Kotlin 2.5.0 is a stable release, and not before the main study's write-up
  ([B-19](B-19-write-up.md)). If SKIE supports 2.5.0 by then, B2 joins and the round is the whole
  matrix again; that is decided here when the item starts, not assumed now.
- Not covered: changing anything in the main study. Its verdicts stand on 2.4.20 with D8, and this round's
  numbers are reported as a round of their own.

- AC: on stable Kotlin 2.5.0, with D8 reverted on a branch (the public `Item` `@Serializable`), B3
  builds and carries the spec on the simulator; or the failure is recorded verbatim.
- AC: the bridges that build on 2.5.0 are listed with their versions; SKIE's support is checked by
  building, not read off its compatibility page.
- AC: the round's pre-registration (which questions, which arms, against which thresholds) is written
  into BRIEF.md as an amendment set of its own before its first measurement.
- Anchors: `shared/src/commonMain/kotlin/bench/shared/Item.kt`, `bridge-swift-export/`,
  `gradle/libs.versions.toml`.
