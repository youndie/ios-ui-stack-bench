---
id: B-09
title: "Variant B1 — KMP + SwiftUI over the Objective-C export: the full spec"
status: done
priority: P1
size: M
stage: stage-1-build
blocked_by: [B-07]
---

# B-09 — Variant B1 — KMP + SwiftUI over the Objective-C export, the full spec

The shared app spec of the brief in arm B1: the same SwiftUI views as A over the shared module,
through the plain Objective-C export and a hand-written Swift adapter that turns the module's
`StateFlow` into the `@Observable` model the views read ([B-02](B-02-swift-bridge.md)). This is the
arm C is paired with: the same bridge, so B1→C is the cost of Compose UI alone. The list screen — rows with a title,
two text lines, a numeric badge and a 48 pt thumbnail, a search field that filters on every
keystroke — and the detail screen pushed from a row, with a large image, about ten text blocks and
one looping 2 s animation. The instrumentation of [B-05](B-05-hello-world-variants.md), unchanged.

- **The decision and its reason.** The idiomatic default of the stack, and nothing beyond it: no
  hand-tuning another variant does not get. Every non-default flag goes into `docs/flags.md`
  (target) with the reason; an Info.plist key the platform requires for a capability (research
  §1.6, §1.7) is a flag too, and is applied — or withheld — identically wherever it is meaningful.
- Not covered: parity across variants — that is [B-11](B-11-parity-check.md), which may send work
  back here.

- AC: Release build with the pinned toolchain and the brief's fairness flags; runs on the simulator; installs on
  both devices via free provisioning once the device work starts (amendment A1.3).
- AC: 2,000 rows reachable by scrolling, filtering by the shared test vector of
  [B-07](B-07-fixture-and-shared-module.md) gives the expected ids, the detail animation loops.
- AC: the signposts "first frame" and "list populated" fire once per launch, in that order.
- Anchors: `apps/b1-objc/` (target).

---

## Findings — 2026-10-10

**Done on the simulator** (the devices come with the owner's go, amendment A1.3). Nothing in B1 had
to change for the full spec. The views are arm A's (B-08), and the adapter in
`apps/b1-objc/iosApp/BenchApp.swift` already maps every field. The checks below were done by driving
the app.

- The list shows the fixture from the Kotlin `Catalog`, with thumbnails and badges.
- Typing `amber harbor` calls `Catalog.filter` on every keystroke through the adapter, and leaves
  the vector's five rows. The Kotlin filter itself is held to all 18 vectors by `FilterVectorTest`.
- A row opens its detail, which shows the ten paragraphs carried over the Objective-C export as
  `[String]`. The square is turning (two screenshots 0.7 s apart differ).
- `launch`, `firstFrame` and `listPopulated` fire once, in that order.
- `scripts/build-arms.sh` prints the same shared klib for B1 as for B2, B3 and C.
- **The adapter, as it stands.** Over the Objective-C export the `StateFlow` arrives as
  `Kotlinx_coroutines_coreStateFlow`. Values come through a `FlowCollector` as `Any?` and are cast to
  `[Item]`. `collect` is a completion-handler call that runs for the app's lifetime. The emission
  happens on the main thread, because `filter` is called there and the flow has no dispatcher.
- **Not walked here:** scrolling to row 2,000. It is in the list by construction; B-13's S2 flings
  scroll it.
