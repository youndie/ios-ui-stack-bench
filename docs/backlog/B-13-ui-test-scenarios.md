---
id: B-13
title: "The UI-test scenarios S1–S4, one target driving all three variants by bundle id"
status: open
priority: P1
size: M
stage: stage-2-harness
blocked_by: [B-11]
---

# B-13 — The scenarios S1–S4

The brief's four scenarios, scripted: S1 cold start (terminate, wait 10 s, launch, record until the
list is populated); S2 fling (20 flings down, 20 up, fixed velocity via
`XCUICoordinate.press(forDuration:thenDragTo:withVelocity:thenHoldForDuration:)`); S3 filter (a
12-character query typed one key at a time with fixed delays, then cleared); S4 navigation churn
(50 push/pop cycles on the detail screen). No manual scrolling, no Maestro.

Two things the brief does not say and the numbers depend on:

- **S1 is a warm launch in Apple's own terms** — terminate and relaunch leaves the app's pages
  cached ([research §1.3](../research/research-architecture.md)). The protocol is kept as written;
  what it is called in the write-up is settled in B-01.
- **The same gesture does not move the same content.** `UIScrollView` and Compose's `LazyColumn`
  apply different fling physics, so 20 flings at one velocity travel different distances and render
  different numbers of rows. The hitch time ratio is per second and survives that; the comparison
  of work does not. Every fling therefore records the distance travelled and rows rendered (from the
  first and last visible index, signposted) beside its frame data.

- **The decision and its reason.** One UI-test target, apps addressed by bundle id, so that the
  runner is one install whatever [B-04](B-04-free-provisioning-probe.md) found about the cap.
  Scenario phase markers are signposts emitted by the app, not timestamps taken by the runner,
  because the runner's clock is in another process.

- AC: each scenario runs unattended on both devices against each variant and leaves phase markers
  in the app's log.
- AC: S2 logs distance travelled and first/last visible index per fling; S4 logs the
  `phys_footprint` sample at the end of each cycle.
- AC: a scenario run whose phase markers are incomplete is marked invalid by the reader, not
  silently shortened.
- Anchors: `harness/` (target).
