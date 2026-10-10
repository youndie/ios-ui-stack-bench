---
id: B-05
title: "Hello-world arms A, B1, B2, B3 and C with the instrumentation the study will measure through"
status: done
priority: P0
size: M
stage: stage-0-gate
blocked_by: [B-02]
---

# B-05 — Hello-world arms, instrumented

The brief's P0: no variant is built in full until RQ0 is green on a device. This item builds the
smallest three apps that carry **everything the study measures through** and nothing it measures:
a list of a few rows, a pushed detail screen, and the instrumentation — identical `os_signpost`
points (launch, first frame, list populated, scenario phase markers), the `CADisplayLink`
frame-interval logger, the `phys_footprint` sampler (`task_vm_info`, every 250 ms) and a switch that
injects a 50 ms main-thread stall on demand.

- **The decision and its reason.** The instrumentation is one Swift package used by every
  arm, not three copies: a logger that differs between variants is a variable the brief never
  declared. In C it is called from the hosting `UIViewController`, which is the only Swift code C has.
- The sampler and the logger run off the main thread where they can, and their own cost is
  measured in [B-16](B-16-dry-run-and-the-ruler.md) (the brief's kill criterion 5 is about the test
  runner, but an instrument that costs a frame is the same contamination from inside).
- The bundle ids are fixed here and never changed (a free account may create 10 App IDs per 7 days;
  [B-04](B-04-free-provisioning-probe.md) installs them on the devices later, amendment A1.3). Since amendment A1.1
  there are five arms: A, the three bridge arms of [B-02](B-02-swift-bridge.md) — B1 Objective-C
  export with a Swift adapter, B2 SKIE, B3 Swift export — and C. Each bridge is proven here, on the
  hello-world, because a bridge that cannot carry a `StateFlow` to the SwiftUI views on the pinned
  Kotlin should be known before P1, not inside it (research Risk 8).
- Not covered: the app spec (2,000 items, thumbnails, search). That is P1, after the gate.

- AC: all five build in Release with the pinned toolchain and the fairness flags of the brief
  (K/N release, static, dead-code stripping; Swift `-O` and whole-module optimisation), and every
  non-default flag is listed in `docs/flags.md` (target) — including any 120 Hz or design-system
  Info.plist key that [research §1.6 and §1.7](../research/research-architecture.md) shows to be
  needed.
- AC (amendment A1.3: simulator now, devices when the owner starts the device work): each arm runs
  on the simulator and logs its signposts, frame intervals
  and footprint samples through the same code path; the log format is the one the readers of
  [B-14](B-14-trace-export-and-readers.md) will parse.
- AC: the three bridge arms show the same state in the same SwiftUI views; each arm's adapter is the
  only Swift code that differs between them, and it is short enough to read in the pull request.
- AC: the stall switch is reachable from the UI-test runner (a launch argument), so the gate can
  inject it without a build of its own.
- Anchors: `apps/a-native/`, `apps/b1-objc/`, `apps/b2-skie/`, `apps/b3-swift-export/`,
  `apps/c-kmp-cmp/`, `shared/`, `instrumentation/` (all target).

---

## Findings — 2026-10-10

**Done on the simulator; the devices come with the owner's go (amendment A1.3).** All five arms
build in Release with Xcode 27.0 (27A266a), Kotlin 2.4.20, CMP 1.12.1 and SKIE 0.10.15, and run on
the iOS 27 simulator with the same instrumentation: `scripts/build-arms.sh`, then
`scripts/sim-smoke.sh` (the pull request carries both logs). No simulator number is recorded here.

What exists now:

| Piece | Where |
|---|---|
| The shared Kotlin module: `Catalog` (parse, filter, `StateFlow`), `Item`, a test of the filter (mutation-checked: `ignoreCase = false` fails it) | `shared/` |
| One framework module per bridge, and arm C's Compose UI | `bridge-objc/`, `bridge-skie/`, `bridge-swift-export/`, `compose-ui/` |
| The instrumentation every arm compiles — signposts, NDJSON log, frame logger, footprint sampler, stall injector; its log format is in the file's header | `apps/common/Instrumentation/Bench.swift` |
| The SwiftUI views of A, B1, B2, B3, and the fixture loader | `apps/common/ListUI/`, `apps/common/Fixture/` |
| Five Xcode projects, generated from the KMP wizard's template | `apps/generate_projects.py`, `apps/*/iosApp.xcodeproj` |
| Each arm's own code: A's Swift catalog, B1/B2/B3's adapters, C's host | `apps/*/iosApp/BenchApp.swift` |
| The non-default flags | `docs/flags.md` |

Decisions made on the way, each where it will be read:

- **One source, not one package** for the instrumentation and the views: the shared Swift files are
  synchronized folders compiled into each app's own module, so no arm pays a module boundary the
  others do not. The item said "one Swift package"; the reason it says so — one implementation,
  not five — is kept (research D2).
- **`listPopulated` is the first display-link tick after the first row appeared.** A row "appears"
  (SwiftUI `onAppear`, Compose's first composition of the row) before the frame that shows it; the
  first version marked the appearance and logged `listPopulated` before `firstFrame` in two arms.
  Both markers are now quantised to frames the same way in every arm (`Bench.swift` header).
- **Swift export cannot compile kotlinx-serialization on stable Kotlin (KT-87791)**; the shared
  module keeps serialization internal, for every arm (research §1.11, D8 — the owner may overturn
  it). **SKIE 0.10.15 refuses Kotlin 2.4.21**, so development stays on 2.4.20 (I14, B-01 pins).
- Bundle ids `io.github.youndie.iosbench.{a,b1,b2,b3,c}`, fixed; a Personal Team id goes into the
  git-ignored `apps/*/Configuration/Local.xcconfig`.

Not covered here: the full spec (B-07–B-10, B-20, B-21), devices and signing (B-04, B-06), CI (B-22).
