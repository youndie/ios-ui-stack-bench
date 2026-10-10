---
id: B-13
title: "The UI-test scenarios S1–S4, one target driving every arm by bundle id"
status: done
priority: P1
size: M
stage: stage-2-harness
blocked_by: [B-10, B-20, B-21]
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

- AC: each scenario runs unattended on both devices against each of the five arms and leaves phase
  markers in the app's log; a session installs and drives only the arms the session plan of
  [B-01](B-01-pins-and-the-amendment-window.md) gives it, with A in every session.
- AC: S2 logs distance travelled and first/last visible index per fling; S4 logs the
  `phys_footprint` sample at the end of each cycle.
- AC: a scenario run whose phase markers are incomplete is marked invalid by the reader, not
  silently shortened.
- Anchors: `harness/` (target).

**Blocker changed 2026-10-10:** it was B-11 (parity), whose check runs on the devices. Since
amendment A1.3 the harness is built on the simulator before the device work, and what the scenarios
need is the five arms, not their parity; the blockers are now the last arms built (B-10, B-20, B-21).
Parity still comes before any measurement — that order is B-16's and B-17's.

---

## Findings — 2026-10-10

**Done on the simulator; all four scenarios pass against all five arms** (20 of 20 runs, logs in
the pull request). The devices come with the owner's go (amendment A1.3).

- **The harness** is `harness/`: a UI-testing bundle with **no host app**
  (`harness/generate_project.py`, checked by `make check`, compiled in CI). It drives an arm by
  bundle id. On a device the harness adds the runner and nothing else, which matters under the
  three-app cap (research §1.5). `harness/run.sh <arm> <scenario> [launch arguments]` builds it once
  and runs one scenario. The arm and its launch arguments reach the tests through
  `TEST_RUNNER_BENCH_BUNDLE` and `TEST_RUNNER_BENCH_LAUNCH_ARGS`.
- **The scenarios** (`harness/HarnessUITests/Scenarios.swift`), as the brief has them:
  - S1 terminate, 10 s, launch;
  - S2 20 + 20 flings with `press(forDuration:thenDragTo:withVelocity:thenHoldForDuration:)` at
    2,500 px/s;
  - S3 `amber harbor` typed one key per 0.3 s, then deleted the same way;
  - S4 50 push/pop cycles on the first item.

  Elements are found by the fixture's text, which is the same in every arm.
- **Phase markers come from the app** (`Bench.swift` header):
  - `scenario:<name>` at launch;
  - `query` on every change of the search text (S3: 24 = 12 keys + 12 deletions);
  - `detailAppeared` / `detailDisappeared` (S4: 50 each);
  - `scroll` begin/end on every transition between scrolling and resting (S2: 40 each). SwiftUI
    logs the content offset at each transition (`onScrollPhaseChange`). Compose logs the first and
    last visible item and the first one's offset in pixels (`isScrollInProgress`).

  The probes run on transitions only, never per frame. **"First and last visible index" for the
  SwiftUI arms is derived** from the offset and the row height by the reader. SwiftUI does not hand
  it over without a per-change callback, and that callback would be a cost only those arms paid.
- **Three things the simulator taught, each now in the code with its reason:**
  1. **XCUITest waits for SwiftUI's animations to settle, not for Compose's.** With a 2 s pause, C's
     40 flings ran into each other: one `scroll` begin, one end, a list that barely moved net. The
     pause is now a fixed 5 s for every arm, longer than any arm's deceleration, and every fling
     logs its own begin and end.
  2. **Compose Multiplatform exposes `OutlinedTextField` to accessibility as a text view**, not a
     text field. The harness looks for a search field, then a text view.
  3. **After the query is cleared, Compose's keyed `LazyColumn` keeps the row that was on top**
     (item 59 of `amber harbor`), where SwiftUI's `List` goes back to the top. That is each stack's
     default and stays. S3 asserts that the field is empty, not that the first item is back. It
     also means S3's last frames render different rows in C than in A — descriptive S3 (A1.2) says so.
- **Left to [B-14](B-14-trace-export-and-readers.md):** "a run whose phase markers are incomplete is
  marked invalid by the reader". The markers exist and are counted above; rejecting a short run is
  the reader's job.
- Not done here: recording with `xctrace` — also B-14's.
