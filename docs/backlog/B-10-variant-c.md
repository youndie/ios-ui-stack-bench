---
id: B-10
title: "Variant C — KMP + CMP: the full spec"
status: wip
priority: P1
size: M
stage: stage-1-build
blocked_by: [B-07]
---

# B-10 — Variant C — KMP + CMP, the full spec

The shared app spec of the brief in variant C: Compose Multiplatform `LazyColumn`, navigation inside Compose, one full-screen `ComposeUIViewController`. The list screen — rows with a title,
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
- Anchors: `apps/c-kmp-cmp/` (target).
