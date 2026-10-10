---
id: B-21
title: "Variant B3 — KMP + SwiftUI over Swift export: the full spec, or the reason it cannot be built"
status: open
priority: P1
size: M
stage: stage-1-build
blocked_by: [B-07]
---

# B-21 — Variant B3 — KMP + SwiftUI over Swift export

The third bridge arm of amendment A1.1 ([B-02](B-02-swift-bridge.md)): the same SwiftUI views as A,
B1 and B2, over the same compiled shared module, exported with Kotlin's own Swift export instead of
an Objective-C header. Flows reach Swift as `AsyncSequence`; it needs direct integration
(`embedSwiftExportForXcode`), erases generics to their upper bounds, exports only final classes
inheriting from `Any` — and it is **Alpha**, with breaking changes expected
([research §1.8](../research/research-architecture.md)).

- **The decision and its reason.** Swift export as its documentation configures it, at the pinned
  Kotlin, with nothing hand-patched. The shared module is not reshaped to suit it: if a type the
  module exposes cannot be exported, B3's adapter works around it in Swift and the workaround is
  listed — the module is the same bytes for every arm, or the A→B comparison stops being one.
  **Corrected 2026-10-10 by [B-05](B-05-hello-world-variants.md):** on stable Kotlin, Swift export
  cannot compile kotlinx-serialization's API (KT-87791, fixed in 2.5.0), so the shared module keeps
  serialization internal for every arm (research §1.11, D8). The rule that survives is the one in
  bold: the same bytes for every arm.
- **A B3 that cannot carry the spec is a result, not a delay.** If the hello-world in
  [B-05](B-05-hello-world-variants.md) or this item cannot build or cannot observe the state, B3 is
  reported "not measured" with the failure verbatim and the Kotlin version it was hit on, and the
  study goes on with B1, B2 and C (research Risk 8). No other arm waits for it.
- Not covered: Swift export together with Compose Multiplatform — C uses the Objective-C export.

- AC: Release build with the pinned toolchain and the brief's fairness flags, installed on both
  devices — or a `not measured` record in this file and BRIEF.md with the build or runtime failure,
  under `logs/b-21/`.
- AC: the shared module's klib digest equals the other Kotlin arms' ([B-07](B-07-fixture-and-shared-module.md)).
- AC: 2,000 rows reachable by scrolling, filtering by the shared test vector gives the expected ids,
  the detail animation loops; "first frame" and "list populated" fire once per launch, in that order.
- Anchors: `apps/b3-swift-export/` (target), `logs/b-21/`.
