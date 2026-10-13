---
id: research-architecture
title: iOS UI stack benchmark — the evidence the study starts from
type: research
status: active
date: 2026-10-10
---

# Research: what the study starts from

One app, three times — native SwiftUI (A), a shared Kotlin module under the same SwiftUI views (B),
the same module under Compose Multiplatform (C) — measured on physical iPhones for size, startup,
scroll smoothness and memory. The questions, thresholds and kill criteria are the frozen
[source brief](source-brief.md); what the study decided around them is [BRIEF.md](../../BRIEF.md).

This document records what was **verified** before any code existed — read in a source, an
artefact or on the Mac that will drive the devices — what follows from each fact, the places
where the frozen brief cannot be applied as written, and the risks with the machinery that answers
each. Anything not verified is called a hypothesis and names the item that will check it. It is
amended, never rewritten: when a device proves a line here wrong, the correction goes at that line.

Everything below was checked on **2026-10-10**. Apple's documentation pages were read through their
JSON mirrors (`developer.apple.com/tutorials/data/documentation/<path>.json`), because the HTML is
rendered by script; two Medium articles were read in a browser after Medium refused the fetcher.

---

## 1. Verified facts

### 1.1 The prior work, as its sources report it

The brief's Context summarises four sources. Read at the source, three of the summaries are right,
and three details are not — which matters, because the write-up will set its numbers beside them.

| Fact | Where verified |
|---|---|
| **Commencis** (Ali Taha Dinçer, 2024-01-29): one coin-list app built 15 ways; iOS on the "iPhone 15 Pro Max" **simulator** after writing results on a physical iPhone 11 failed; release mode; FPS from `CADisplayLink`, memory from in-app kernel calls, each from a separate build; a manual 40-scroll gesture; one chart per variant, repetitions never mentioned; CMP for iOS "still in its alpha stage", no version given | Part 1 ("Testing", "FPS Measurer", "Memory Measurer") and Part 2 introduction, medium.com/commencis, URLs in the brief's Sources |
| Commencis' **375–400 MB is one variant: a CMP list inside UIKit navigation** (`KMPiOSCMPUIKit`). The full-screen CMP variants settle at about 275–300 MB; KMP with UIKit 110–120 MB; plain UIKit 40–50 MB. App sizes: UIKit 631 KB, SwiftUI 950 KB, KMP 7.2 MB, CMP 29.4 MB. Freezes reported in four CMP variants; one crashed after 7–10 scrolls | Part 2, §3.1, 3.3, 3.5, 3.6, 3.9 |
| **Software Mansion** (Artur Gęsiarz, 2026-07-02): CMP **1.10.0** with Kotlin 2.3.0 against React Native with Expo; iPhone 13 mini (A15, 4 GB), iPhone 16, iPhone 17; Release, Ad-Hoc | swmansion.com blog, URL in the brief |
| Software Mansion's CMP figures: average footprint 157.0 / 230.2 / 251.4 MB; **800–870 ms is time to initial display** (870 / 822 / 802), time to full display 1 203–1 364 ms; 11.2 MB download, 32.1 MB installed. No native baseline; frame rate measured on Android only | same, "iOS memory", "startup", "app size" |
| **Zhuravko** (2026-06-22): **Swift 29.10 MiB, CMP 55.75 MiB** of "Persistent Heap + VM" in Instruments (1.9×); **Swift bundle 484 KB, CMP 38 MB**. One profiling session per app (32 s and 39 s); the device is never named, nor whether it was a simulator | medium.com/@zhuravl321, "iOS: Swift vs Compose Multiplatform", "Stability and App Size" |
| **JetBrains** (2025-05-06, CMP 1.8.0): "startup time is comparable to native apps", with no numbers; CMP adds "about 9 MB" against a SwiftUI app with the same UI — **without saying whether download or install size, which app, or which architecture** | blog.jetbrains.com, "Performance that's ready for production" |

**Consequence 1 — the brief's Context carries three errors the write-up must not repeat.** The
brief prints Zhuravko's pairs in the reverse order ("55.75 vs 29.10 MiB … 38 MB vs 484 KB" under
"Swift vs CMP"); it attributes Commencis' 375–400 MB to "CMP" when it is the hybrid embedding the
brief's own non-goals exclude; and it calls Software Mansion's figure "time to first frame" without
naming it TTID. The frozen text stays as it is. The write-up cites the sources as this table does
([B-19](../backlog/B-19-write-up.md)).

**Consequence 2 — "the consistent signal is a 2–4× memory premium" is not what the sources show.**
Zhuravko measured 1.9× on one metric that is not footprint; Commencis' full-screen CMP against
UIKit is about 6× on a simulator; Software Mansion has no native baseline. The brief's RQ4
thresholds (green ≤ 2×, red > 3×) are therefore a prior of the author's, not a summary of
evidence — which is fine for a pre-registered threshold, and is said once so nobody later cites the
Context as its justification.

**Consequence 3 — the prior CMP numbers describe a different renderer.** Software Mansion measured
CMP 1.10.0. From 1.11.0 CMP renders on a dedicated thread by default and presents through a layer
of its own (§1.4). Whatever C shows on the pinned version, a difference from Software Mansion's
figures cannot be read as a difference between devices or methods alone.

### 1.2 The stand on 2026-10-10

| Fact | Where verified |
|---|---|
| The only Xcode on the driving Mac is `/Applications/Xcode-beta.app`, **Xcode 27.0 build 27A5228h — beta 4** (2026-07-20). The released Xcode 27.0 is build **27A266a** (2026-09-14) | `xcodebuild -version`; `ls /Applications`; developer.apple.com/news/releases; xcodereleases.com `data.json` |
| Xcode 27 deploys to iOS 15–27 and installs and debugs on devices running **iOS 17 or later** | developer.apple.com/support/xcode, Xcode 27 row and legend |
| Paired physical device: **iPhone XS** (`iPhone11,2`, A12, 4 GB, 60 Hz), not connected at the time. No ProMotion device is paired yet; the owner confirmed one will be available | `xcrun devicectl list devices` |
| The iPhone XS runs **iOS 18 at most**: the iOS 26 list starts at iPhone 11 and SE (2nd gen) | support.apple.com/en-us/104985 (iOS 18 models), support.apple.com/en-us/123705 (iOS 26 models) |
| The `xctrace` templates the brief names exist in this Xcode: **App Launch, Animation Hitches, Allocations, CPU Profiler**; so do the instruments **Hitches, VM Tracker, os_signpost, Display** | `xcrun xctrace list templates`, `xcrun xctrace list instruments` |
| Free disk on the Mac: 47 GiB | `df -h /` |

*Since then.*
- The released Xcode 27.0 (27A266a) is installed and pinned.
- Both phones are pinned in BRIEF.md: the XS on iOS 18.7.3, the 17 Pro on iOS 26.6.2. The study
  reads the XS only (A1.7).
- Of the templates above, Allocations exports none of its data on the device. Memory's Instruments
  figure is Activity Monitor's (A1.7).
- The disk ran out once, filled by `xctrace`'s leftovers (§4, risk 6).

**Consequence 1 — nothing may be measured with the installed Xcode.** The brief pins "the latest
stable Xcode"; a beta is neither stable nor what anybody reproducing the study will have. Xcode
27.0 (27A266a) is installed before [B-04](../backlog/B-04-free-provisioning-probe.md), and its build
number, not its marketing version, is the pin.

**Consequence 2 — the two devices will run different iOS major versions.** The older-device slot
is held by an XS on iOS 18; any current ProMotion iPhone runs iOS 26 or later. SwiftUI's `List`,
navigation bar and search field differ between those versions (§1.7). Every RQ compares variants
*within* a device, so the verdicts survive; a sentence comparing devices would compare operating
systems as much as chips, and the write-up says so.

### 1.3 "Cold start" as the brief defines it is a warm launch in Apple's terms

| Fact | Where verified |
|---|---|
| Apple: a launch soon after the app was terminated "is commonly referred to as a 'warm launch'"; a cold launch is one after the app was evicted from memory — for instance after a memory-intensive app — "or a launch immediately after boot". Apple calls them a spectrum | developer.apple.com/documentation/xcode/reducing-your-app-s-launch-time, "Understand cold and warm launch" |

**Consequence.** S1 — terminate, wait 10 s, launch — measures a warm launch: the app's pages, its
frameworks' pages and the dyld closure are still cached. That is a perfectly good repeatable
measurement, and it is the one the brief's thresholds were written for; the brief's word for it is
not Apple's. Twenty real cold launches per variant would need twenty reboots or a memory-pressure
step that adds a variable of its own. The protocol stays; what it is called is settled in
[B-01](../backlog/B-01-pins-and-the-amendment-window.md) (§2, I8).

### 1.4 Hitches: Apple's bands, and what each instrument can see

| Fact | Where verified |
|---|---|
| Hitch time ratio, ms per second of animation: under 5 good; 5–10 noticeable, investigate; 10 or more, act now. The "good / warning / critical" labels are the session's recap | WWDC20 "Eliminate animation hitches with XCTest" (10077), developer.apple.com/videos/play/wwdc2020/10077; tech talk 10855 |
| A **second Apple scale** exists for the Organizer's hitch rate: ≤ 10 good, ≤ 25 warning, ≤ 50 critical | developer.apple.com/documentation/xcode/understanding-hitches-in-your-app |
| `XCTOSSignpostMetric.scrollingAndDecelerationMetric` (iOS 15+) reports hitch time ratio for **UIKit-instrumented** scroll intervals; custom intervals need `os_signpost(.animationBegin…)` | developer.apple.com/documentation/xctest/xctossignpostmetric/scrollinganddecelerationmetric; WWDC20 10077 |
| `XCTHitchMetric` exists from **iOS 26.0** | developer.apple.com/documentation/xctest/xcthitchmetric |
| `XCTMemoryMetric` reports the **difference** in physical memory before and after the measured block; `XCTApplicationLaunchMetric` ends at the first frame (or at main-thread responsiveness with `waitUntilResponsive`) | developer.apple.com/documentation/xctest/xctmemorymetric; .../xctapplicationlaunchmetric/init(waituntilresponsive:) |
| CMP 1.12.1 renders through Skia on Metal, driven by **its own `CADisplayLink`**. With `parallelRendering = true` — **the default since 1.11.0** — composition, layout and recording run on the main thread and GPU encoding on a serial queue `RenderingDispatchQueue`; frames are presented by setting an IOSurface as `contents` of a `CMPMetalLayer : CALayer` inside a `CATransaction`, on the main thread. With `false` it is a plain `CAMetalLayer` | `JetBrains/compose-multiplatform-core@a1a7f3533363aa93849541cf451af2363fc2070a!/compose/ui/ui/src/iosMain/kotlin/androidx/compose/ui/window/SurfaceMetalRedrawer.ios.kt`, `JetBrains/compose-multiplatform-core@a1a7f3533363aa93849541cf451af2363fc2070a!/compose/ui/ui/src/iosMain/kotlin/androidx/compose/ui/window/MetalView.ios.kt`, `JetBrains/compose-multiplatform-core@a1a7f3533363aa93849541cf451af2363fc2070a!/compose/ui/ui/src/iosMain/kotlin/androidx/compose/ui/uikit/ComposeContainerConfiguration.ios.kt` (tag v1.12.1); CMP CHANGELOG 1.11.0, "Migration Notes / iOS" |
| A developer report (Aug 2026, unanswered): Animation Hitches records late frames of an `MTKView`, `XCTHitchMetric` records nothing for it | developer.apple.com/forums/thread/842848 |

**Consequence 1 — the brief's thresholds are WWDC20's scale**, which is the right one for an
animation interval; "Apple's 'good' band" in the write-up cites WWDC20 10077 and not the
Organizer page, whose numbers are twice as lenient.

**Consequence 2 — the XCTest metrics cannot be the instrument here.** The scroll metrics see UIKit
scroll views, and C's `LazyColumn` is not one; `XCTHitchMetric` needs iOS 26, which the XS cannot
run; `XCTMemoryMetric` is a delta, and RQ4 needs a peak. The brief's choice of `xctrace` plus an
in-app logger is the one that can work on both devices and in every arm.

**Consequence 3 — the brief's named risk is smaller than it looked, and still unproven.** On
CMP ≥ 1.11, C's frames reach the screen as ordinary Core Animation commits, so Animation Hitches
*should* account for them as it does for A and B (**hypothesis H1**, checked by the injected stall
in [B-06](../backlog/B-06-rq0-the-gate.md)). `parallelRendering` stays at its default; it is
recorded as a pin, because a change of default between CMP versions changes what C is.

**H1 confirmed on the iPhone XS, 2026-10-11 ([B-06](../backlog/B-06-rq0-the-gate.md),
[GATE.md](../../GATE.md)).** On the self-scrolling run, Animation Hitches shows the injected 50 ms
stall as hitches at the stall in C, as in every other arm, and shows nothing at 0 ms. The in-app
logger agrees in every arm. The newer device is not measured (BRIEF.md A1.7).

### 1.5 A free Apple ID: what it allows

| Fact | Where verified |
|---|---|
| A Personal Team may have **up to 3 apps installed per device**, profiles expire **7 days** after issue, up to **10 App IDs** per 7 days, up to 3 devices | developer.apple.com/support/compare-memberships, "Enable a personal team in Xcode"; Apple DTS in developer.apple.com/forums/thread/745359 calls these limits "not well documented" |
| The UI-test runner is a separately signed app with its own bundle id (`…UITests.xctrunner`) and App ID; **whether it occupies one of the three install slots is not documented** anywhere found. The device log filtered by `MIFreeProfileValidatedAppTracker` lists the bundle ids counted against the limit | github.com/callstack/agent-device/issues/145; velog.io/@adbr (Xcode error "The maximum number of apps for free development profiles has been reached") |
| Builds installed by Xcode carry `get-task-allow` regardless of configuration; Allocations and Leaks fail without it, Time Profiler usually works. No list per instrument is published; nothing found for Animation Hitches or App Launch, and nothing specific to a Personal Team | developer.apple.com/forums/thread/745789; .../thread/681687 |
| `XCUICoordinate.press(forDuration:thenDragTo:withVelocity:thenHoldForDuration:)` exists, now in the `XCUIAutomation` framework; velocity in pixels per second; no iOS availability gate in the Xcode 27 header | developer.apple.com/documentation/xcuiautomation/xcuicoordinate; the `XCUIAutomation` framework header `XCUICoordinate.h`, line 46, in Xcode-beta 27.0 |

**Consequence — the protocol as written may not fit on a device.** Three variants installed
together plus a runner is four apps against a cap of three, if the runner counts. The brief rotates
A→B→C inside a session and forbids reinstalling mid-session; its own mitigation ("one UI-test
target driving all variants by bundle ID") reduces the runners to one but still needs four
installs. [B-04](../backlog/B-04-free-provisioning-probe.md) answers it on the device before any
code (§2, I5).

**Amended 2026-10-10, the same day: the cap now binds whatever the runner does.** The owner split B
into three arms, one per Swift bridge (BRIEF.md A1.1, D5 below), so the study has five apps — A,
B1, B2, B3, C — against three slots. No session can hold every arm, and the brief's rotation
A→B→C inside one session becomes a set of sessions that share an anchor arm: A is installed in
every session, each other arm is compared with A inside its own session, and two non-anchor arms
are compared only through A, or by sharing a session. B1 and C share one, because B1→C is the
brief's "cost of Compose UI" (D5). Which sessions exist depends on whether the runner takes a slot:
two free slots beside A, or one.

**Measured 2026-10-11 on both devices ([B-04](../backlog/B-04-free-provisioning-probe.md)): one
slot.** The runner takes a slot, so a session holds the runner and two arms. That cannot hold A, B1
and C together. The owner chose pairs, five sessions per device: {A, B1}, {A, B2}, {A, B3}, {A, C} and
{B1, C}, with the phones on charge throughout ([BRIEF.md](../../BRIEF.md) A1.5).

| Fact | Where verified |
|---|---|
| The cap is 3 apps per device, enforced at install: the fourth is refused with "This device has reached the maximum number of installed apps using a free developer profile", listing the three identifiers that hold the slots | `stand/b-04/2026-10-11-xs-install-cap.log` |
| The UI-test runner (`io.github.youndie.iosbench.harness.xctrunner`) is refused by the same limit with three arms installed, and installs once one is removed | `stand/b-04/2026-10-11-xs-runner.log` |
| A Release build signed by the Personal Team carries `get-task-allow = true`; its profile is issued for 7 days (created 2026-10-11, expires 2026-10-18) | `codesign -d --entitlements`, `security cms -D` of `embedded.mobileprovision`, same day |
| `xctrace record --launch` records App Launch, Animation Hitches and Allocations of arm A on the iPhone XS. The Hitches trace holds `hitches-summary` and the `hitches-*-interval` tables; the Allocations trace exports no allocation table through `xctrace export --toc` | `stand/b-04/2026-10-11-xs-xctrace.log` |
| `xctrace` lists a paired device under "Devices Offline", and times out "waiting for device to boot", until something opens its tunnel; one `devicectl` request does | the same log |
| `xcodebuild test` cannot install the runner on either device: "Root install style is not supported on this device". The message is the system CoreDevice framework's (642.16, installed by Xcode 27.0 and loaded by any Xcode), so Xcode 26.6 fails the same way. The trigger is the `DSTROOTPath` key that build-for-testing writes into the `.xctestrun` (`/tmp/Harness.dst`): with it, XCTHarness takes the internal install style, which needs an internal iOS build. A copy of the `.xctestrun` without the key runs S1–S4 of arm A on the XS with Xcode 27.0 | `stand/b-04/2026-10-11-xs-runner-dstroot.log`, `stand/b-04/2026-10-11-xs-runner-xcode26.log`; the strings of the system CoreDevice framework 642.16 and of Xcode 27.0's XCTHarness framework, read on the Mac |
| The runner needs UI automation allowed on the phone: until it is, it starts and fails "Timed out while enabling automation mode" | `stand/b-04/2026-10-11-xs-runner-dstroot.log` |

**Consequence — the harness runs a device from a patched `.xctestrun`**, and every arm and the
runner stay on the pinned Xcode 27.0. `harness/run.sh` and `harness/parity.sh` drop the one key
before `test-without-building`; the simulator path is unchanged.

### 1.6 120 Hz: the key C cannot run without

| Fact | Where verified |
|---|---|
| Without `CADisableMinimumFrameDurationOnPhone = YES` in Info.plist, Core Animation on a ProMotion iPhone "won't access higher frame rates (above 60Hz)" for `CADisplayLink` callbacks and `CAAnimation`; the system handles frame pacing of UIKit, SwiftUI and `CAAnimation` animations itself | developer.apple.com/documentation/bundleresources/information-property-list/cadisableminimumframedurationonphone; developer.apple.com/documentation/quartzcore/optimizing-iphone-and-ipad-apps-to-support-promotion-displays |
| A developer report: `scrollViewDidScroll` at 120 Hz while the app's own `CADisplayLink` ran at 70–80 Hz, until the key was added | developer.apple.com/forums/thread/792011 |
| **CMP refuses to start without the key**: `enforceStrictPlistSanityCheck` defaults to `true`, and a missing or false key is an `error(...)` naming "inadequate performance on iPhones with high refresh rate". CMP's display link asks for `screen.maximumFramesPerSecond` | `JetBrains/compose-multiplatform-core@a1a7f3533363aa93849541cf451af2363fc2070a!/compose/ui/ui/src/iosMain/kotlin/androidx/compose/ui/uikit/PlistSanityCheck.ios.kt`, `JetBrains/compose-multiplatform-core@a1a7f3533363aa93849541cf451af2363fc2070a!/compose/ui/ui/src/iosMain/kotlin/androidx/compose/ui/window/MetalView.ios.kt` |
| The KMP wizard's iOS app ships the key, `true`, in both its shared-UI and native-UI templates | `Kotlin/kmp-wizard@d7c757a51afd9b0968da0d3c11f9cf05696894c8!/iosApp/iosApp/Info.plist` (shared UI), `Kotlin/kmp-wizard@8fa355754f55454e0e2e72a6c0b4e29052ed5b7d!/iosApp/iosApp/Info.plist` (native UI) |

**Consequence 1 — the key is C's idiomatic default**, not a tuning: the template ships it and the
framework will not run without it.

**Consequence 2 — A and B need it too, or the study's own frame logger lies on the 120 Hz
device.** The logger is a `CADisplayLink`; without the key it is held near 60 Hz while SwiftUI's
scrolling runs at 120, and it would report A's and B's frames at half the rate C's are reported
at. The decision (D3) is the key in every arm, listed as a flag, with its cost stated: on
A and B it changes the logger's cadence and the detail screen's custom animations, not the system's
scrolling — which [B-16](../backlog/B-16-dry-run-and-the-ruler.md) checks with the logger on and
off.

### 1.7 Liquid Glass, and why a first-screen pixel diff cannot pass A against C

| Fact | Where verified |
|---|---|
| Built with the iOS 26+ SDK, standard SwiftUI components adopt Liquid Glass automatically — `NavigationStack` bars, toolbars, search in toolbars; lists get larger rows and padding and rounder section corners | developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass |
| The opt-out `UIDesignRequiresCompatibility` is temporary, and "the system ignores this key when you build for iOS 27 or later" | developer.apple.com/documentation/bundleresources/information-property-list/uidesignrequirescompatibility |
| Compose Multiplatform does not draw Liquid Glass: JetBrains says it comes from the native `TabView`, `NavigationStack` and toolbar APIs | kotlinlang.org/docs/multiplatform/ios-liquid-glass.html |

**Consequence 1 — with the pinned Xcode 27 SDK, A and B have Liquid Glass on the newer device and
the old design on the XS (iOS 18), and C has Material on both.** There is no switch: the opt-out is
ignored for iOS 27 builds, and building with an older Xcode would break the brief's toolchain rule.
The glass is part of what "native" costs on a current iPhone, and it is reported as such — not
removed, and not counted as a defect of C.

**Consequence 2 — the brief's parity rule needs a number and a region.** A first-screen pixel diff
between a SwiftUI screen with glass chrome and a Compose screen with Material chrome fails at any
small tolerance, for a reason no build effort removes — and kill criterion 3 counts build days.
Parity is checked on geometry by number (item count, row height, thumbnail and type size) and by
pixels over the list content; how the chrome is treated is an amendment
([B-11](../backlog/B-11-parity-check.md), §2, I12).

### 1.8 The Swift bridge for B and C

| Fact | Where verified |
|---|---|
| **Plain Objective-C export**: generics only on classes, not interfaces, so `StateFlow<T>` reaches Swift as a non-generic protocol needing casts and a collector; `suspend` becomes a completion handler | kotlinlang.org/docs/native-objc-interop.html, "Generics", "Suspending functions" |
| The KMP wizard's native-UI template applies **no SKIE and no Swift export**, links `isStatic = true`, Kotlin 2.4.20, CMP 1.12.1 | `Kotlin/kmp-wizard@8fa355754f55454e0e2e72a6c0b4e29052ed5b7d!/sharedLogic/build.gradle.kts`, `Kotlin/kmp-wizard@8fa355754f55454e0e2e72a6c0b4e29052ed5b7d!/gradle/libs.versions.toml` |
| **SKIE 0.10.15** (2026-09-25) adds Kotlin 2.4.20; its compatibility page still says up to 2.4.10; Kotlin 2.4.21 is not mentioned. `StateFlow` → `SkieSwiftStateFlow`, an `AsyncSequence` with its type argument | github.com/touchlab/SKIE/releases; skie.touchlab.co/changelog/0.10.15; skie.touchlab.co/features/flows |
| **Swift export is Alpha**, "breaking changes are expected"; flows become `AsyncSequence`; direct integration only; nothing published on coexistence with a CMP framework | kotlinlang.org/docs/native-swift-export.html; kotlinlang.org/docs/whatsnew2420.html |

**Consequence.** The recommendation for [B-02](../backlog/B-02-swift-bridge.md) was the plain
Objective-C export with a thin hand-written Swift adapter to `@Observable`: it is what the
template generates, it adds no compiler plugin whose support has to track the Kotlin pin (SKIE
does not yet claim the latest stable Kotlin, 2.4.21), and the A→B delta then measures what most KMP
apps actually ship. Swift export is excluded on its own label. The choice is the owner's.

**Superseded 2026-10-10 by the owner's decision: all three are measured**, each as its own B arm
(BRIEF.md A1.1, D5). The paragraph above is kept because it is still why B1, the Objective-C export,
is the arm C is paired with, and why SKIE constrains the Kotlin pin (§2, I14). Swift export's
"Alpha" now matters as a risk, not as an exclusion (Risk 8).

### 1.9 The fairness flags are already the defaults, and the size breakdown needs a link map

| Fact | Where verified |
|---|---|
| KGP's default is a dynamic framework (`isStatic = false`); the wizard sets `isStatic = true` | `JetBrains/kotlin@v2.4.20!/libraries/tools/kotlin-gradle-plugin/src/common/kotlin/org/jetbrains/kotlin/gradle/targets/native/NativeBinaries.kt:326`; `Kotlin/kmp-wizard@8fa355754f55454e0e2e72a6c0b4e29052ed5b7d!/sharedLogic/build.gradle.kts` |
| A static Kotlin framework is an archive; its code, and Skiko's native code with it, is linked into the app's main executable — there is no Kotlin `.framework` in the `.app` | `JetBrains/kotlin@v2.4.20!/kotlin-native/backend.native/compiler/ir/backend.native/src/org/jetbrains/kotlin/backend/konan/Linker.kt:27-34` |
| Kotlin/Native's dead-code elimination runs in release builds by default (no flag); for a static framework the final `-dead_strip` happens in the app's link | `JetBrains/kotlin@v2.4.20!/kotlin-native/backend.native/compiler/ir/backend.native/src/org/jetbrains/kotlin/backend/konan/driver/phases/TopLevelPhases.kt:514` |
| `DEAD_CODE_STRIPPING` is set to `YES` by the iOS SDK's default properties, for every configuration | the iOS SDK's SDKSettings.plist, key DefaultProperties, in Xcode-beta 27.0 — to be re-read in the pinned Xcode |
| `LD_GENERATE_MAP_FILE` writes a map of every symbol and its origin | developer.apple.com/documentation/xcode/build-settings-reference, "Write Link Map File" |

**Consequence 1 — the brief's fairness flags cost nothing to honour**: release K/N, static, dead-code
stripping and Swift `-O` with whole-module optimisation in Release are the template's and the SDK's
defaults. They are still listed, with their sources, so a reader sees that no variant was tuned.

**Consequence 2 — the brief's per-component breakdown ("app binary, Kotlin framework, Skiko")
cannot be read off file sizes.** It is taken from the final link map, summed by object origin
([B-12](../backlog/B-12-rq1-size.md), D6).

### 1.10 Kotlin/Native memory, as `phys_footprint` will see it

| Fact | Where verified |
|---|---|
| Default GC in Kotlin 2.4: concurrent mark & sweep (`cms`), non-generational, parallel mark, on its own thread, triggered by heuristics or a timer | kotlinlang.org/docs/native-memory-manager.html, "Garbage collector"; kotlinlang.org/docs/native-binary-options.html |
| K/N uses its own paged allocator over `mmap`, tagged `246` (`mmapTag`), visible in VM Tracker | same pages, "Memory consumption" |
| Defaults the study keeps: `objcDisposeOnMain=true`, `appStateTracking=disabled`, `latin1Strings=false`, `smallBinary=false`, `enableSafepointSignposts=false` | kotlinlang.org/docs/native-binary-options.html |

**Consequence.** B's and C's heap is dirty anonymous memory, so it counts in `phys_footprint`, and
Allocations shows it as anonymous VM regions under tag 246 rather than as Kotlin objects — which is
what makes the VM Tracker cross-check meaningful for B and C and useless for attributing objects.
Because the collector runs on a timer and on pressure, a peak sampled every 250 ms depends on when
the GC ran; RQ4's peak is read from the same 250 ms series in every arm, and the GC
timing is a reason for its spread, not a variable to tune.

### 1.11 What the bridges compile against, found by building them (B-05)

| Fact | Where verified |
|---|---|
| SKIE 0.10.15 **refuses to configure** with Kotlin 2.4.21: "SKIE 0.10.15 does not support Kotlin 2.4.21", listing 2.4.20 as the newest it supports | the Gradle configuration of `bridge-skie` with Kotlin 2.4.21, 2026-10-10 (B-05) |
| Swift export on Kotlin **2.4.20 and 2.4.21** generates Swift for kotlinx-serialization-core that does not compile: `invalid redeclaration of 'decodeSequentially()'` and four more, each an opt-in interface member with a default emitted twice | the B3 build, both versions, 2026-10-10 (B-05) |
| The defect is **KT-87791** ("[Swift Export] OptIn interface member with default implementation fails to compile"), fixed and "available in 2.5.0-Beta1"; KT-88225, reporting exactly this redeclaration, was closed as its duplicate | youtrack.jetbrains.com/issue/KT-87791, /issue/KT-88225 |
| With kotlinx-serialization's types out of the shared module's **public** API (the `@Serializable` class internal, the public `Item` a plain class), Swift export on 2.4.20 compiles and B3 builds and runs | the B3 build after the change, 2026-10-10 (B-05) |
| Swift export hands Swift the `StateFlow<List<Item>>` as a typed `KotlinTypedStateFlow<[Item]>`, iterated with `asAsyncSequence()`; over the Objective-C export (B1) it is the non-generic `Kotlinx_coroutines_coreStateFlow`, collected through a `FlowCollector` with `Any?` values | the generated `SharedLogic.swift` and `Shared.h` of B-05's builds |

**Consequence 1 — I14 is settled by the toolchain, not by preference.** No stable Kotlin satisfies
both B2 and B3 untouched: SKIE stops at 2.4.20, and Swift export's fix is in 2.5.0. Development is
on **2.4.20** (the newest SKIE accepts) with D8's workaround for B3; the pin is still B-01's.

**Consequence 2 — the workaround changes the shared module for every Kotlin arm**, which keeps the
rule that matters — B1, B2, B3 and C link the same module bytes — and breaks the item text B-21 was
written with ("the shared module is not reshaped to suit it"). It is recorded as D8 and flagged to
the owner; the alternatives are B3 "not measured" until Kotlin 2.5.0 is stable and SKIE supports
it, or a different Kotlin for B3 alone, which would make B3's module different bytes.

### 1.12 What Instruments records on the simulator (B-14)

| Fact | Where verified |
|---|---|
| `xctrace record --template 'Animation Hitches'` on the iOS 27 simulator ends with "Hitches is not supported on this platform" and records no hitches | Xcode 27.0 (27A266a), iPhone 17 Pro simulator, 2026-10-11 (B-14) |
| `xctrace record --template 'App Launch' --launch -- <bundle id>` on the same simulator reaches its time limit, prints "ending recording", and does not exit; it had to be interrupted | same |

**Consequence.** Nothing about the Instruments half of the study can be developed or checked on the
simulator: not the recording, not the export schemas, not the readers. That half moves to
[B-24](../backlog/B-24-xctrace-record-and-readers.md), after RQ0 ([B-06](../backlog/B-06-rq0-the-gate.md))
has produced real device traces. The in-app half — the logger, the footprint sampler, the markers
and their reader — works on the simulator and is built there (B-14).

### 1.13 How reproducible the arms' builds are (B-26)

| Fact | Where verified |
|---|---|
| Two clean device archives (new derived data, Kotlin build directories deleted, Gradle cache off) of A, B1 and B3 give byte-identical main executables | `scripts/measure_size.py`, Xcode 27A266a, Kotlin 2.4.20, 2026-10-11 (B-26) |
| Two clean archives of B2 and C give executables of identical size that differ in a few hundred bytes: the `LC_UUID`, and bytes inside `__TEXT,__objc_stubs`, `__TEXT,__stubs` and, for C, `__TEXT,__text`. C's Kotlin framework is byte-identical in both builds, so the difference arises in the app's final link | `cmp -l` of the two executables mapped onto `otool -l`'s sections, same day |
| The `zip -9` proxy of those two builds differs by at most a few tens of bytes | `sizes.csv` of the same run |

**Consequence.** RQ1 is decided on build 1 of each arm, and its thresholds are megabytes. A link
that is not byte-reproducible, but is reproducible in size, cannot move a verdict. That holds as long
as the two builds' proxies stay within bytes of each other, and the size tooling prints that gap on
every run. The digest that B-10 saw move for B3 did not move between clean builds here.

---

## 2. Where the frozen brief cannot be applied as written

The brief cannot be edited, and these cannot be left to the first number. Each is settled as an
amendment in BRIEF.md by [B-01](../backlog/B-01-pins-and-the-amendment-window.md), or recorded as
"left as written" with the reason. **None of them asks for a threshold to move.**

| # | Where | The problem | What has to be decided |
|---|---|---|---|
| I1 | Kill criterion 4 | "After 20 runs" — but S2–S4 have 10 runs per variant, 9 counted. For RQ3, RQ4 and the hitch half of RQ5, "after 20 runs" never happens | the run count at which kill criterion 4 is applied to each scenario |
| I2 | Runs and statistics | "A bootstrap 95 % CI for each A–B and A–C difference … the CI must not cross the threshold" fits RQ2 and RQ5, whose thresholds are differences. RQ3's are absolute values of C, RQ3's "no hitch ≥ 100 ms in any run" is a maximum, RQ4's are a ratio to A and a growth within C, and RQ1 has no sample at all | the interval each RQ is decided with: CI of C's median (RQ3), CI of the ratio (RQ4), a count (max hitch), none (RQ1, deterministic) |
| I3 | RQ4, RQ5 | No device is named. RQ2 says "older device", RQ3 "both" | the device(s) for RQ4 and RQ5 |
| I4 | RQ0 vs kill criterion 2 | RQ0 is green only if both instruments see the stall; kill criterion 2 fires only if neither does. If only the in-app logger sees it for C, RQ0 is grey and RQ3 is still owed — but its thresholds are in Animation Hitches' unit, and the logger as specified reports frame-time percentiles, not ms/s | a hitch time ratio computed from the logger's frame intervals, defined before any number ([B-14](../backlog/B-14-trace-export-and-readers.md)), and which instrument RQ3 uses in that case |
| I5 | Risks, free provisioning | The cap of 3 is confirmed (§1.5). With five arms since A1.1, no session holds every arm, and the brief's rotation inside a session with no mid-session reinstall cannot cover them | the session plan, once [B-04](../backlog/B-04-free-provisioning-probe.md) has said whether the runner takes a slot: which arms share a session (A in all of them; B1 with C), how the order rotates inside and across sessions, and how a comparison between two arms in different sessions is read — through A only, with A's figures from both sessions side by side |
| I6 | Kill criterion 5 | "The UI-test runner's CPU or memory overhead" — the runner's own figures are another process and never appear in the app's footprint or CPU; contamination is the shift in the **app's** figures with the runner attached | which of the two is compared with the 10 % line |
| I7 | RQ4 | "Growth over 50 push/pop cycles < 5 MB after warm-up" — S4 is 50 cycles in all, and where warm-up ends is not said | the cycle at which the baseline is read (for instance after cycle 5) and whether growth is last-minus-baseline or a slope |
| I8 | S1 | "Cold start" is Apple's warm launch (§1.3) | keep the protocol; name it in the write-up |
| I9 | RQ1 | "i.e. JetBrains' ~9 MB claim reproduces" — JetBrains does not say what its 9 MB measures (§1.1), so a green on `zip -9` neither reproduces nor refutes it | the write-up's wording; the thresholds stand |
| I10 | RQ3 | "Apple's 'good' band" — two Apple scales exist (§1.4); the brief's numbers are WWDC20's | the citation; the thresholds stand |
| I11 | Context | Three source details are wrong (§1.1) | nothing to amend; the write-up cites the sources directly |
| I12 | Fairness, parity | "Screenshot diff of the first screen within a small tolerance" has no number, and A against C cannot pass a whole-screen diff on the iOS 27 SDK (§1.7) | the tolerance, the region, and the treatment of the system chrome, before the first diff |
| I13 | Prerequisites | "Latest stable Xcode": the Mac has only a beta (§1.2). Latest stable Kotlin is 2.4.21 (2026-10-08) and CMP 1.12.1 (2026-09-22); SKIE does not yet claim 2.4.21 | pins in BRIEF.md, by build number and commit |
| I14 | Prerequisites, A1.1 | B2 needs SKIE, and SKIE 0.10.15 claims Kotlin 2.4.20, not the latest stable 2.4.21 (§1.8). The shared module must be one Kotlin build for every Kotlin arm | the Kotlin pin: the newest version all three bridges compile against — checked by building the hello-world arms, not read off a compatibility page. If that is 2.4.20, it is a deviation from "latest stable" stated as such. **Checked in B-05 (§1.11):** SKIE refuses 2.4.21, and Swift export needs D8 on both |
| I15 | RQ1, RQ4, RQ5 | "MB" is not defined: 2 MB, 12 MB, 20 MB, 5 MB and 50 MB read as 10^6 or 2^20 bytes differ by 4.9 % | proposed in `analysis/verdicts.py`: decimal, 10^6 bytes, as Apple's size reports count |

---

## 3. Decisions

### D1. A public repository in English, laid out as a measurement study

Owner's answer to the brief's open decision, 2026-10-10: `ios-ui-stack-bench`, public; documents,
code, commits and pull requests in English. The brief is frozen byte for byte in
[source-brief.md](source-brief.md) and `make check` holds it; the rest follows the layout of a
measurement study (BRIEF.md, a file-per-item backlog, raw logs as the deliverable).

### D2. One instrumentation package for every arm

Signposts, the frame logger, the footprint sampler and the stall switch are one Swift package
linked by every arm — A, B1, B2, B3 and C ([B-05](../backlog/B-05-hello-world-variants.md)). Rejected: three
implementations "the same" — an instrument that differs between variants is an undeclared variable.
The price: in C the instruments live in the hosting view controller and see Compose only through
signposts the Kotlin side emits through the same API.

### D3. `CADisableMinimumFrameDurationOnPhone = YES` in every arm *(a flag beyond A's default)*

Brief: idiomatic defaults, every non-default flag listed. Decision: the key in every arm. Why: C
cannot start without it (§1.6), so it is C's default; without it in A and B the study's frame logger
runs at 60 Hz on a 120 Hz screen and reports their frames on a different basis from C's. The price:
A and B carry one key their template does not, which may change the cadence of their custom
animations; it is listed in the flags document (docs/flags.md, once a variant exists) and its effect on A is measured with the logger on and
off in [B-16](../backlog/B-16-dry-run-and-the-ruler.md). Confirmed or overturned by the owner in
B-01.

### D4. Liquid Glass stays where the platform puts it *(proposal, settled in B-01 and B-11)*

The idiomatic default of A and B on the iOS 27 SDK includes Liquid Glass on the newer device and
there is no supported opt-out (§1.7). It is not removed and not imitated in C; parity is defined on
geometry and on the list content, and the asymmetry is a stated qualification of every RQ3 result on
the newer device. Rejected: building with Xcode 26 to use the opt-out — it breaks the brief's
toolchain rule and pins the study to a design Apple has already removed the switch for.

### D5. B is three arms, one per Swift bridge *(owner, 2026-10-10; deviation from the brief)*

Brief: one bridge, chosen once and kept identical in B and C, because the A→B delta measures the
binding tool as much as Kotlin/Native. Decision ([B-02](../backlog/B-02-swift-bridge.md), BRIEF.md
A1.1): measure all three — **B1** Objective-C export with a hand-written Swift adapter, **B2** SKIE,
**B3** Swift export — each its own app ([B-09](../backlog/B-09-variant-b.md),
[B-20](../backlog/B-20-variant-b2-skie.md), [B-21](../backlog/B-21-variant-b3-swift-export.md)).
The brief's own risk becomes the subject: the spread between B1, B2 and B3 is what the binding tool
costs.

- **One Kotlin module, three bindings.** The shared module's compiled library (`.klib`) is the same
  bytes in every Kotlin arm; what differs is the framework each bridge produces from it and the thin
  Swift adapter that turns its state into the `@Observable` model the identical SwiftUI views read.
  The klib digest is checked equal across arms, the framework digests are recorded per arm
  ([B-07](../backlog/B-07-fixture-and-shared-module.md)).
- **C is paired with B1.** C hosts Compose and barely crosses the bridge; it is built with the
  Objective-C export, the template's default, so B1→C is the brief's "cost of Compose UI" with
  nothing else changing.
- **RQ5 is answered per bridge, never as the best of three.** Picking the bridge that came out
  greenest would turn three tries into one verdict, so the write-up prints three RQ5 verdicts against
  the same thresholds, and RQ1's B − A likewise.
- The price: five apps against a cap of three (§1.5, I5), three more builds to keep at parity, a
  Kotlin pin bounded by SKIE (I14), and an Alpha toolchain in one arm (Risk 8).

### D6. The size breakdown comes from the link map

`LD_GENERATE_MAP_FILE = YES` on the app target, the map summed by object origin — app, Kotlin
(stdlib, coroutines, serialization, the shared module), Skiko and Compose, Swift runtime. Rejected:
file sizes inside the `.app`, which hold no Kotlin or Skiko file once linking is static (§1.9).

### D7. Install the released Xcode 27.0 (27A266a) before anything runs on a device

§1.2. The beta stays installed only if disk allows; nothing is built for a measurement with it.

### D8. kotlinx-serialization stays inside the shared module *(B-05; kept by the owner on 2026-10-10)*

Brief: B and C's logic is "shared Kotlin module, kotlinx-serialization, `StateFlow`" — still true.
Decision: the fixture is decoded into an `internal` `@Serializable` class and mapped to a public,
plain `Item`, so no kotlinx-serialization type is in the module's public API. Why: Swift export on
every stable Kotlin cannot compile kotlinx-serialization's exported API (§1.11, KT-87791), and this
is the one change that lets B3 build without making its module differ from B1's, B2's and C's. The
price: every Kotlin arm pays one extra object per item at load (the DTO, then the `Item`) — the same
in all four, and arm A maps its `Codable` struct to the views' row type too. Rejected: B3 "not
measured" until Kotlin 2.5.0 (it would hold B3 hostage to two releases, Kotlin's and SKIE's); a
newer Kotlin for B3 alone (its module would no longer be the others').

**The owner kept D8 on 2026-10-10**, and asked for B3 to be tried again on Kotlin 2.5.0 without it.
That is a later round of its own, not a pin change: SKIE refuses every Kotlin after 2.4.20, so B2
cannot be built there ([B-23](../backlog/B-23-kotlin-2-5-round.md)).

---

## 4. Risks and open questions

**Risk 1. The install cap makes the interleaved protocol impossible.** Five arms since A1.1 do not
fit three slots in any case, and if the runner occupies a slot only two arms fit beside it. A
comparison between arms measured in different sessions mixes the arms with the sessions.
Mitigation: A is the anchor installed in every session, every other arm is read against A from its
own session, and a cross-session comparison is printed with A's figures from both sessions beside
it, so a session effect shows up as a moving A rather than as an arm effect. Before that, [B-04](../backlog/B-04-free-provisioning-probe.md) measures the cap with
empty apps before any study code, logs the refusal text and the counted bundle ids
(`MIFreeProfileValidatedAppTracker`), and proposes the protocol change as an amendment while the
window is open. Bundle ids are fixed in B-04 and never change, because App IDs are also capped
(10 per 7 days).

*Outcome (2026-10-11 to 13).* The cap is three, and the runner takes one (B-04). Sessions were pairs
until A2.2 moved every verdict-deciding scenario off the runner. After that they were triples with
A in each: {A, C}, {A, B1, B2}, {A, B3, C} (A2.5). The cross-session figures for A are in
`logs/b-17/`.

**Risk 2. Animation Hitches does not see C's frames the way it sees A's.** C presents through a
`CATransaction` since CMP 1.11 (§1.4), so the hypothesis is that it does. Mitigation: the injected
50 ms stall in every arm, and a 0 ms stall through the same path that must *not* register
([B-06](../backlog/B-06-rq0-the-gate.md)); the logger-derived hitch ratio defined beforehand (I4).

*Outcome.* Animation Hitches sees C's stall as it sees A's (H1 confirmed on the XS, §1.4,
[GATE.md](../../GATE.md)). The logger turned out to be the weaker instrument: it sees main-thread
stalls only, not render-server hitches (B-16, A2.2).

**Risk 3. The instruments are part of the subject.** A `CADisplayLink` logger can raise the
display's rate by asking for it; a 250 ms sampler and signposts cost something; in C a second
display link runs beside CMP's. Mitigation: A with the instruments on and off, against the ruler,
in [B-16](../backlog/B-16-dry-run-and-the-ruler.md); the logger's `preferredFrameRateRange` is
recorded in every log header.

*Outcome.* The instruments moved A's launch by less than the ruler resolves (B-16). A larger risk
came from elsewhere: **the UI-test runner** raised the app's own CPU time and memory, by different
amounts per stack (kill criterion 5). Memory, CPU and smoothness are therefore measured without it
(A2.2).

**Risk 4. The same fling moves different amounts of content.** `UIScrollView` and `LazyColumn`
apply different deceleration, so one velocity renders different numbers of rows. Hitch time ratio is
per second and survives it; the work done does not. Mitigation: distance travelled and first/last
visible index recorded per fling ([B-13](../backlog/B-13-ui-test-scenarios.md)) and printed beside
RQ3.

*Outcome.* The verdict-deciding smoothness runs use the app's own scroll (S2p, A2.2): the same
40 steps of about a screen in every arm, with Animation Hitches recording. Real flings remain as
the logger's cross-check on S2.

**Risk 5. Profiles expire after 7 days.** A session straddling an expiry reinstalls mid-session.
Mitigation: the brief's own — reinstall everything at the start of every session — plus the
profile's expiry printed in the session header, and a session refused to start within a day of it.

*Outcome.* Every session ran inside one profile's life (issued 2026-10-11, valid to 2026-10-18).
Another way to lose the apps turned up instead. Uninstalling every app of the Personal Team drops
the developer trust, and the phone then refuses new installs until the owner trusts it again
(B-17). The sessions now always leave one app installed.

**Risk 6. The Mac runs out of disk.** 47 GiB free must hold the released Xcode, the Kotlin/Native
toolchain, three apps' builds and the `.trace` bundles. Mitigation: a bundle is deleted only after
its CSVs are exported and its `sha256` written into `logs/`; the session command checks free space
before it starts.

*Outcome.* The disk did fill. `xctrace` leaves raw `instruments*.ktrace` files of 1–2.5 GB each in
`$TMPDIR` and never removes them; tens of GB built up and killed a gate run. `harness/recording.py`
now deletes them after every recording, and deletes the trace bundle once it is exported and hashed
(B-06).

**Risk 7. Thermal drift.** The brief's rotation, `thermalState` logging and discard rule stand;
[B-16](../backlog/B-16-dry-run-and-the-ruler.md) shows A's time-ordered series so that the drift the
rotation is meant to cancel is seen, not assumed.

*Outcome.* Every attempt of B-16's ruler and of the three sessions stayed `nominal`; no run was
repeated for heat. The phone was on charge throughout (A1.5).

**Risk 8. Swift export is Alpha, and B3 may not build the spec.** Its documentation expects breaking
changes and limits what it exports (§1.8); a `StateFlow` reaching Swift as something the adapter
cannot observe, or a build failure on the pinned Kotlin, would leave B3 empty. Mitigation: B3's
hello-world is part of the gate ([B-05](../backlog/B-05-hello-world-variants.md)), so a toolchain
that cannot carry the spec is known before P1; if it fails, B3 is reported "not measured" with the
failure verbatim — a blocker, which is a weaker claim than a measured result — and B1, B2 and C go on.

*Outcome.* B3 builds and is measured. Kotlin 2.4.20's Swift export needed workaround D8 for a
redeclaration (KT-87791). In S1, B2 (SKIE) and B3 (Swift export) draw their first frame earlier
than A and B1, and their list later after it. They reach a populated list at about A's time, which
is what RQ5 reads (`trace_process_to_first_frame_ms` against `trace_process_to_list_ms` in
`logs/b-17/xs-2` and `xs-3`). Their verdicts are in README.md. A round on Kotlin 2.5.0 without D8
is B-23.

**Open question 1 — which ProMotion iPhone, on which iOS.** Its iOS major version decides whether
`XCTHitchMetric` is available as a third cross-check on that device (it is not on the XS) and how
far it is from the XS's iOS 18. Pinned in [B-01](../backlog/B-01-pins-and-the-amendment-window.md).

*Answered, then set aside.* It is an iPhone 17 Pro on iOS 26.6.2 (23G90), pinned in BRIEF.md. The owner
reads every question on the XS (A1.7), so it is B-18, a question for the owner.

---

## 5. What happens next

*Rewritten 2026-10-13; the original plan is in the history.* The gate passed (B-06), the window
closed, and everything the iPhone XS can answer is measured: RQ1 (B-12, B-31), RQ2–RQ5 (B-17), with
the method amended as §4's outcomes describe. What is left:
- [B-19](../backlog/B-19-write-up.md), the write-up. It reports one verdict per question, negative
  results included, and keeps every late amendment beside the figure it changed.
- [B-18](../backlog/B-18-runs-on-the-newer-device.md), the newer device, which waits for the owner.
- [B-23](../backlog/B-23-kotlin-2-5-round.md), the Kotlin 2.5.0 round for Swift export.
