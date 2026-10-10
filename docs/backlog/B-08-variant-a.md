---
id: B-08
title: "Variant A — Native: the full spec"
status: done
priority: P1
size: M
stage: stage-1-build
blocked_by: [B-07]
---

# B-08 — Variant A — Native, the full spec

The shared app spec of the brief in variant A: SwiftUI `List` and `NavigationStack`, `Codable`, `@Observable`. The list screen — rows with a title,
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
- Anchors: `apps/a-native/` (target).

---

## Findings — 2026-10-10

**Done on the simulator** (the devices come with the owner's go, amendment A1.3).

- **The views.** `apps/common/ListUI/Views.swift`, compiled into A and the three B arms. It uses
  `NavigationStack`, a plain `List`, and `.searchable`.
  - A row is a 48 pt thumbnail, the title, two lines and a capsule badge.
  - The detail screen is a 240 pt image, the title, a square turning once every 2 s (`repeatForever`)
    and the item's ten paragraphs, in a `ScrollView`.
  - Thumbnails are the bundled PNGs through `UIImage(named:)`, the system's cached lookup.
  - Nothing beyond the stack's defaults.
- **Arm A's logic** (`SwiftCatalog.swift`) decodes `paragraphs` too. The filter is unchanged and
  still matches all 18 vectors.
- **`RowItem` gained `paragraphs`**, so the B arms' adapters map one more field. That is the one change
  to them, and the build needed it; their own items (B-09, B-20, B-21) still check them against the spec.
- **Walked on the simulator.** Every check below was done by driving the app, not by reading code.
  - The list shows the fixture with thumbnails and badges.
  - Typing `amber harbor` leaves the five rows the vector names (59, 669, 1231, 1681, 1798).
  - One more key leaves none.
  - A row opens its detail, which shows the image, the ten text blocks and the square turning (two
    screenshots 0.7 s apart differ).
  - `launch`, `firstFrame`, `listPopulated` fire once, in that order (`scripts/sim-smoke.sh`).
- **Not walked here:** scrolling to the 2,000th row. The list is the fixture without paging, so every
  row is in it by construction, but the scroll itself is exercised by the S2 flings of
  [B-13](B-13-ui-test-scenarios.md), not by this item.
- **Seen on the way:** the system design puts A's search field at the bottom of the screen, in Liquid
  Glass (research §1.7). That is the default, and it is left alone.
