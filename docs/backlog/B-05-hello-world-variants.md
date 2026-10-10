---
id: B-05
title: "Hello-world A, B and C with the instrumentation the study will measure through"
status: open
priority: P0
size: M
stage: stage-0-gate
blocked_by: [B-02, B-04]
---

# B-05 — Hello-world A, B and C, instrumented

The brief's P0: no variant is built in full until RQ0 is green on a device. This item builds the
smallest three apps that carry **everything the study measures through** and nothing it measures:
a list of a few rows, a pushed detail screen, and the instrumentation — identical `os_signpost`
points (launch, first frame, list populated, scenario phase markers), the `CADisplayLink`
frame-interval logger, the `phys_footprint` sampler (`task_vm_info`, every 250 ms) and a switch that
injects a 50 ms main-thread stall on demand.

- **The decision and its reason.** The instrumentation is one Swift package used by all three
  variants, not three copies: a logger that differs between variants is a variable the brief never
  declared. In C it is called from the hosting `UIViewController`, which is the only Swift code C has.
- The sampler and the logger run off the main thread where they can, and their own cost is
  measured in [B-16](B-16-dry-run-and-the-ruler.md) (the brief's kill criterion 5 is about the test
  runner, but an instrument that costs a frame is the same contamination from inside).
- The bundle ids are those fixed in [B-04](B-04-free-provisioning-probe.md); the bridge is
  [B-02](B-02-swift-bridge.md)'s.
- Not covered: the app spec (2,000 items, thumbnails, search). That is P1, after the gate.

- AC: all three build in Release with the pinned toolchain and the fairness flags of the brief
  (K/N release, static, dead-code stripping; Swift `-O` and whole-module optimisation), and every
  non-default flag is listed in `docs/flags.md` (target) — including any 120 Hz or design-system
  Info.plist key that [research §1.6 and §1.7](../research/research-architecture.md) shows to be
  needed.
- AC: each installs on both devices via free provisioning and logs its signposts, frame intervals
  and footprint samples through the same code path; the log format is the one the readers of
  [B-14](B-14-trace-export-and-readers.md) will parse.
- AC: the stall switch is reachable from the UI-test runner (a launch argument), so the gate can
  inject it without a build of its own.
- Anchors: `apps/a-native/`, `apps/b-kmp-swiftui/`, `apps/c-kmp-cmp/`, `shared/`,
  `instrumentation/` (all target).
