---
id: source-brief
title: The brief as received, verbatim
type: research
status: active
date: 2026-10-10
---

> **The frozen text, and the only copy of it in this repository.** Below the marker is the brief
> exactly as it arrived on 2026-10-10, byte for byte — including the backslash-escaped tildes of
> the editor it was exported from: 13 229 bytes, `sha256
> 3437dbc9ad7fa7fbc8a40009421e3900b75193924780f4fabf6dd091950f0aa3`. `make check` hashes every
> byte after the marker against the record line in [BRIEF.md](../../BRIEF.md)
> (`scripts/brief_freeze.py`).
>
> **Nothing below the marker may be edited, including typography and whitespace — and including
> where it turns out to be wrong.** What the study *decided* — the pins, the answers to what the
> brief believed, the amendments — is [BRIEF.md](../../BRIEF.md). Which of the brief's premises
> survived contact with a source or a device is
> [research-architecture.md](research-architecture.md): §1 there records the premises that did
> not survive, and §2 the places where this text cannot be applied as written and has to be
> settled by amendment before the first measurement.

<!-- ---8<--- everything after this line is the received text, byte for byte ---8<--- -->
# iOS UI stack benchmark — research brief

Oct 10, 2026 · @Pavel

## Context

There is no public, reproducible, on-device measurement of native SwiftUI vs KMP + SwiftUI vs KMP + Compose Multiplatform on a current toolchain. This study builds one app three times and measures size, startup, scroll smoothness and memory on physical iPhones, with methodology and raw data committed next to every number.

What exists today and why it is not enough:

- **Commencis, Jan 2024** — 15 variants of one coin-list app. iOS measured on a simulator, single manual run per variant, FPS and memory from different builds, CMP for iOS still in Alpha. Reported freezes and 375–400 MB footprint for CMP vs 40–50 MB for UIKit; none of it is reproducible.
- **Software Mansion, Jul 2026** — KMP + CMP 1.10.0 vs React Native on three iPhones, release builds. CMP: 157–251 MB average footprint, \~800–870 ms to first frame, download size 11.2 MB. No native baseline and no iOS frame metrics; authored by a React Native shop.
- **Daniil Zhuravko, Jun 2026** — Swift vs CMP currency converter: 55.75 vs 29.10 MiB persistent memory, 38 MB vs 484 KB bundle. One short session, toy app, Swift side with zero dependencies.
- **JetBrains, May 2025 (CMP 1.8.0)** — claims startup comparable to native and \~9 MB added vs a SwiftUI app with the same UI. Vendor numbers, no published methodology.

The consistent signal is a 2–4× memory premium for CMP on iOS. Scroll smoothness against native, on a device, with a repeatable gesture, is unmeasured.

## Subjects

Three apps implement one spec. B and C share the same Kotlin module byte-for-byte, so A→B isolates the cost of the Kotlin/Native runtime and the Swift bridge, and B→C isolates the cost of Compose UI.

| Variant | Logic | UI | Delta it isolates |
| --- | --- | --- | --- |
| A — Native | Swift, Codable, `@Observable` | SwiftUI `List`, `NavigationStack` | Baseline |
| B — KMP + SwiftUI | Shared Kotlin module, kotlinx-serialization, `StateFlow` | Same SwiftUI views as A | A→B: K/N runtime, GC, ObjC/Swift bridge |
| C — KMP + CMP | Same shared module as B | CMP `LazyColumn`, navigation inside CMP, one full-screen `ComposeUIViewController` | B→C: Skia renderer, Compose runtime |

### Shared app spec

1. **Data** — 2,000 items from a bundled JSON fixture (\~1 MB), parsed at launch. No network.
2. **List screen** — rows with title, two text lines, a numeric badge and a 48 pt thumbnail from a set of 50 bundled PNGs. A search field filters the list on every keystroke.
3. **Detail screen** — pushed from a row: large image, \~10 text blocks, one looping 2 s animation.
4. **Instrumentation** — identical `os_signpost` points in all three: launch, first frame, list populated, scenario phase markers.

### Fairness rules

- Each variant uses the idiomatic default of its stack. No hand-tuning that the other variants do not get; every non-default flag is listed in the repo.
- Release configuration everywhere. K/N framework built as release, static, with dead-code stripping on; Swift with `-O` and whole-module optimisation.
- Visual parity is checked before any measurement: same item count, same row height in points, screenshot diff of the first screen within a small tolerance.

## Research questions

Thresholds are fixed now, before any code exists. A result between green and red is reported as inconclusive, never rounded towards either side. "Older device" and "newer device" are defined in Methodology.

### RQ0 — Gate: can every metric be captured on a device without a paid Apple account?

- **Green:** all three variants install as Release builds via free provisioning; `xctrace` records App Launch, Animation Hitches and memory footprint for each; an injected 50 ms main-thread stall shows up as a hitch in all three, in both the Instruments trace and the in-app frame logger.
- **Red:** any metric cannot be captured for any variant, or the injected stall is invisible for C. That metric is dropped (see Kill criteria).

### RQ1 — Size: what do KMP and CMP add to an arm64 app?

- **Green:** B − A ≤ 2 MB and C − A ≤ 12 MB on the compressed size proxy, i.e. JetBrains' \~9 MB claim reproduces.
- **Red:** B − A > 5 MB, or C − A > 20 MB.

### RQ2 — Startup: does C reach a populated list as fast as A?

- **Green:** median time to list populated for C ≤ A + 100 ms on the older device.
- **Red:** C > A + 250 ms on the older device.

### RQ3 — Smoothness: does C scroll as smoothly as A?

- **Green:** C's hitch time ratio in the fling scenario < 5 ms/s on both devices (Apple's "good" band), and no single hitch ≥ 100 ms in any run.
- **Red:** C > 10 ms/s on either device (Apple's "critical" band), or any hitch ≥ 250 ms — a Commencis-style freeze.

### RQ4 — Memory: what is C's footprint premium, and does it grow?

- **Green:** C's peak `phys_footprint` in the fling scenario ≤ 2× A, and footprint growth over 50 push/pop cycles < 5 MB after warm-up.
- **Red:** C > 3× A, or growth ≥ 20 MB over 50 cycles.

### RQ5 — Bridge: is shared Kotlin logic free for a SwiftUI UI?

- **Green:** B within +1 ms/s of A on hitch ratio, within +50 ms on time to list populated, and ≤ +20 MB peak footprint.
- **Red:** B worse than A by > 2 ms/s hitch ratio, or > 150 ms startup, or > 50 MB footprint.

## Methodology

Everything runs on physical iPhones in Release builds, driven by scripted gestures, repeated and interleaved across variants. Simulator results are used only for development and are never reported.

### Devices

- **Older device:** a 60 Hz iPhone with 4 GB RAM or less (A15-class or older). Exposes the memory and startup premium.
- **Newer device:** a 120 Hz ProMotion iPhone. Exposes frame-budget problems at 8.3 ms per frame.
- Exact models and iOS versions are recorded per run. Before each session: reboot, Low Power Mode off, battery above 50 %, airplane mode on, device cool to the touch.

### Scenarios

1. **S1 Cold start** — terminate, wait 10 s, launch; record until the list is populated.
2. **S2 Fling** — 20 flings down and 20 up at a fixed velocity via `XCUICoordinate.press(forDuration:thenDragTo:withVelocity:holdDuration:)`. No manual scrolling, no Maestro.
3. **S3 Filter** — type a 12-character query one key at a time with fixed delays, then clear it.
4. **S4 Navigation churn** — 50 push/pop cycles on the detail screen.

### Metrics and tools

| Metric | Primary tool | Cross-check |
| --- | --- | --- |
| Size | Archive with signing disabled, arm64 `.app`: uncompressed bytes and `zip -9` as the download proxy | Per-component breakdown: app binary, Kotlin framework, Skiko |
| Startup | `xctrace` App Launch + signposts for first frame and list populated | In-app `CACurrentMediaTime` deltas from process start |
| Smoothness | `xctrace` Animation Hitches: hitch time ratio in ms/s, longest hitch | In-app `CADisplayLink` frame-interval logger: p50/p95/p99 frame time, % frames over budget |
| Memory | `phys_footprint` from `task_vm_info`, sampled every 250 ms in-app | `xctrace` Allocations / VM Tracker for one run per variant |
| CPU (secondary) | `xctrace` CPU Profiler, total process CPU time per scenario | Baseline run with the app idle, to measure UI-test runner overhead |

### Runs and statistics

- 20 cold starts and 10 runs of each of S2–S4 per variant per device. The first run of each batch is a discarded warm-up.
- Variant order rotates A→B→C, B→C→A, C→A→B to spread thermal drift. `ProcessInfo.thermalState` is logged; runs that leave nominal are discarded and repeated.
- Report median and IQR per variant, plus a bootstrap 95 % CI for each A–B and A–C difference. Red/green is decided on the median, and the CI must not cross the threshold.
- Raw `.trace` hashes, exported CSVs and analysis scripts are committed; numbers in the write-up are regenerated from those files, never typed.

## Kill criteria

1. **No device path.** No physical iPhone is available, or free provisioning cannot run Release builds under Instruments. The project stops; simulator numbers are not published as a substitute.
2. **Blind instrument.** Neither the Animation Hitches instrument nor the in-app frame logger registers the injected stall in C. RQ3 is cancelled rather than replaced by eyeballing or manual scrolling.
3. **Parity not reached.** The three variants do not pass the parity check within 5 working days of build effort. Scope is cut to the list screen only; if that also fails, stop.
4. **Noise floor.** After 20 runs, a metric's within-variant IQR is wider than the A–C gap it is testing. That RQ is closed as inconclusive; no further runs are added to chase significance.
5. **Measurement contamination.** The UI-test runner's CPU or memory overhead exceeds 10 % of the smallest variant's value for a metric. That metric is reported only from in-app logging, or dropped.

## Non-goals

- **Android.** iOS only; Android parity of KMP is already well documented.
- **Other stacks.** No UIKit, Flutter or React Native variants.
- **Hybrid embedding.** No CMP rendered per cell inside a SwiftUI or UIKit list — the Commencis failure mode is a separate question.
- **Tuning contest.** No variant is optimised beyond its idiomatic default to win a metric.
- **Networking and remote images.** Data and images are bundled, so the network stack is not part of the comparison.
- **Exact App Store size.** Without a paid account there is no App Thinning report; size is a stated proxy, not the store figure.
- **Energy, build times, developer experience, "native feel".** Not measured.
- **Upstream fixes.** Findings may become JetBrains tickets later, but filing or fixing them is out of scope here.
- **Generalisation.** Results describe this app on these devices, not "CMP performance" in general.

## Prerequisites, risks and open questions

### Prerequisites

- A Mac with Xcode, a free Apple ID signed in as a Personal Team, and at least one physical iPhone connected by cable with Developer Mode on.
- Toolchain pinned at kickoff to the latest stable Xcode, Kotlin and Compose Multiplatform, and recorded in the repo. No version bumps mid-study.

### Risks

| Risk | Effect | Mitigation |
| --- | --- | --- |
| Free provisioning caps the number of apps installed per device (believed to be 3; verify in RQ0) | 3 variants + a UI-test runner do not fit at once | One UI-test target driving all variants by bundle ID; install variants in batches if needed |
| Free provisioning profiles expire after 7 days | Mid-study reinstall changes the install state | Reinstall all variants at the start of every session, never mid-session |
| Animation Hitches may not see CMP's Metal-layer frames the same way as SwiftUI's | RQ3 compares unlike numbers | Calibration with the injected stall in RQ0; in-app `CADisplayLink` logger as an independent check |
| Thermal throttling during long sessions | Later variants run slower | Rotated order, thermal-state logging, discard non-nominal runs |
| Bridge choice changes B and C results | A→B delta reflects the binding tool, not KMP | Decide once (below) and keep it identical in B and C |

### Open decisions

- [ ] Swift bridge for B and C: plain Objective-C export with a thin Swift adapter, SKIE, or Swift export.
- [ ] Which iPhones are available for the older and newer device slots.
- [ ] Repository name and location; results go to `docs/research/` there.
- [ ] Whether S3 (filter) gets its own red/green or stays descriptive.

## Phases and deliverables

The gate comes first: no variant is built in full until RQ0 is green on a real device.

1. **P0 Gate (RQ0).** Hello-world A, B and C with signposts, frame logger and injected stall; install via free provisioning; record every metric once. Output: `GATE.md` with the verdict per metric.
2. **P1 Build.** Full spec in all three variants; parity check passes. Output: the three apps, the parity screenshots, the list of non-default flags.
3. **P2 Harness.** UI-test scenarios S1–S4, `xctrace` record and export scripts, CSV extraction, analysis script with bootstrap CIs. Dry-run on one device. Output: one command per session that produces CSVs.
4. **P3 Runs.** Full matrix on both devices, rotated order. Output: raw CSVs, trace hashes, session logs with device, iOS version and thermal state.
5. **P4 Write-up.** One red/green/inconclusive verdict per RQ, regenerated from the CSVs, negative results included. Output: `docs/research/<study>/` with brief, methodology, results and raw data.

## Sources

- [Commencis — I made the same app 15 times, Part 2](https://medium.com/commencis/i-made-the-same-app-15-times-here-are-the-results-part-2-experiments-results-27aeb93cb42b)
- [Software Mansion — We Built the Same App in KMP and React Native](https://swmansion.com/blog/we-built-the-same-app-in-kmp-and-react-native-here-s-what-we-found)
- [Daniil Zhuravko — Swift vs Compose Multiplatform](https://medium.com/@zhuravl321/swift-vs-compose-multiplatform-a-real-world-performance-comparison-dff90b0f8522)
- [JetBrains — Compose Multiplatform 1.8.0: iOS is Stable](https://blog.jetbrains.com/kotlin/2025/05/compose-multiplatform-1-8-0-released-compose-multiplatform-for-ios-is-stable-and-production-ready/)
