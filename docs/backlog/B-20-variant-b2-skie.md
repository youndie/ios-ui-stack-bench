---
id: B-20
title: "Variant B2 — KMP + SwiftUI over SKIE: the full spec"
status: open
priority: P1
size: M
stage: stage-1-build
blocked_by: [B-07]
---

# B-20 — Variant B2 — KMP + SwiftUI over SKIE, the full spec

The second bridge arm of amendment A1.1 ([B-02](B-02-swift-bridge.md)): the same SwiftUI views as A
and B1, over the same compiled shared module, with SKIE applied to the framework. SKIE turns the
module's `StateFlow` into `SkieSwiftStateFlow`, an `AsyncSequence` that keeps its type argument
([research §1.8](../research/research-architecture.md)), so B2's adapter to the `@Observable` model
is an `async` loop instead of B1's collector and casts. The list screen, the detail screen and the
instrumentation of [B-05](B-05-hello-world-variants.md), unchanged.

- **The decision and its reason.** SKIE at its defaults: no feature turned on or off that its
  documentation does not turn on for a new project, and every configuration line listed in the flags
  document with its reason. What B2 against B1 measures is the bridge, and a tuned SKIE would measure
  the tuning.
- SKIE bounds the Kotlin pin: 0.10.15 claims Kotlin 2.4.20, not 2.4.21 (research §2, I14). The pin is
  decided in [B-01](B-01-pins-and-the-amendment-window.md) from what B-05 actually compiled; this
  item builds with that pin and never with a Kotlin of its own.
- Not covered: parity — [B-11](B-11-parity-check.md); B2's views must be the same files as A's.

- AC: Release build with the pinned toolchain and SKIE version and the brief's fairness flags;
  runs on the simulator; installs on both devices once the device work starts (amendment A1.3).
- AC: the shared module's klib digest equals B1's and C's ([B-07](B-07-fixture-and-shared-module.md));
  the framework digest is recorded.
- AC: 2,000 rows reachable by scrolling, filtering by the shared test vector gives the expected ids,
  the detail animation loops; "first frame" and "list populated" fire once per launch, in that order.
- Anchors: `apps/b2-skie/` (target).
