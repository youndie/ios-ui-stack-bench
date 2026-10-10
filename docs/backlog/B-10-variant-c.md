---
id: B-10
title: "Variant C — KMP + CMP: the full spec"
status: done
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

---

## Findings — 2026-10-10

**Done on the simulator** (the devices come with the owner's go, amendment A1.3).
`compose-ui/src/commonMain/kotlin/bench/compose/App.kt` uses the stack's idiomatic defaults:
Material 3, a `LazyColumn`, an `OutlinedTextField` that filters on every keystroke, and JetBrains'
navigation-compose with its default transitions. The images are Compose resources drawn with
`painterResource`. Everything sits in one full-screen `ComposeUIViewController` hosted by SwiftUI.

- **Navigation.** It is `navigation-compose` 2.9.2, the newest stable release; 2.10 is still a
  release candidate. It is not in the wizard's shared-UI template, which has one screen. The brief
  asks for navigation inside Compose, and S4 pushes and pops 50 times, so a screen swap without the
  library's transitions would make C's S4 cheaper than A's `NavigationStack` for a reason that is not
  the stack. The detail route carries no argument; the selected item is held in the host's state.
  Listed in `docs/flags.md`.
- **Images.** The 50 thumbnails moved from `apps/common/Fixture/thumbnails/` to
  `apps/common/Thumbnails/drawable/`. That is the same bytes, and `fixtures/generate.py --check`
  still holds them. The SwiftUI arms bundle that folder as plain files. C reads it as a Compose
  resource directory (`customDirectory`), and its framework build copies the files under
  `compose-resources/` in the app. Each app now carries the images exactly once, which was checked
  in the built `.app`s: C has 50 under `compose-resources` and none at the root, A the opposite. The
  BRIEF.md digest of the thumbnails covers the same files under their new path.
- **Walked on the simulator.**
  - The list shows the fixture with thumbnails and badges.
  - Typing `amber harbor` leaves the vector's five rows.
  - A row opens its detail through the navigation controller. The detail shows the image, the ten
    paragraphs and a square that turns (two screenshots 0.7 s apart differ).
  - Back pops to the list, with the query kept (`rememberSaveable`).
  - `launch`, `firstFrame` and `listPopulated` fire once, in order.
- **Not walked here:** scrolling to row 2,000. The row is in the `LazyColumn` by construction, and
  the scroll itself is [B-13](B-13-ui-test-scenarios.md)'s.
