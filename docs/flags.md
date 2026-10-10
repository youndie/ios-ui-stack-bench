# Non-default flags

The brief's first fairness rule: each arm uses the idiomatic default of its stack, and **every
non-default flag is listed here**. "Default" means the KMP wizard's templates at
`Kotlin/kmp-wizard@8fa355754f55454e0e2e72a6c0b4e29052ed5b7d` (native UI) and
`Kotlin/kmp-wizard@d7c757a51afd9b0968da0d3c11f9cf05696894c8` (shared UI), and the SDK's own defaults
for anything a template does not set. The one place the arms' Xcode projects differ is
`apps/generate_projects.py`; everything else comes from the wizard's `project.pbxproj` unchanged.

| Flag | Where | Arms | Why |
|---|---|---|---|
| `CADisableMinimumFrameDurationOnPhone = YES` | `apps/*/iosApp/Info.plist` | A, B1, B2, B3 (C's template ships it) | C cannot start without it; without it in A and B the frame logger runs at 60 Hz on a 120 Hz screen (research §1.6, D3) |
| Bundle ids `io.github.youndie.iosbench.{a,b1,b2,b3,c}` | `apps/*/Configuration/Config.xcconfig` | all | fixed once and never changed: a free account creates 10 App IDs per 7 days (B-05); the template appends `$(TEAM_ID)` instead |
| `PRODUCT_NAME` `BenchA`…`BenchC` | same | all | names; the template's is `KotlinProject` |
| The Kotlin build phase's task and `cd "$SRCROOT/../.."` | `apps/generate_projects.py` | B1, B2, B3, C | one Gradle build for four apps; A has no Kotlin phase. B3 runs `embedSwiftExportForXcode`, as Swift export's documentation says |
| Shared Swift sources (`apps/common/Instrumentation`, `ListUI`, `Fixture`) as synchronized folders | same | all (C without `ListUI`) | one source of the instrumentation and of the SwiftUI views, compiled into each app's own module (research D2) |
| Kotlin **2.4.20**, not the latest stable 2.4.21 | `gradle/libs.versions.toml` | B1, B2, B3, C | SKIE 0.10.15 refuses 2.4.21 at configuration; the pin is B-01's (research §1.11, I14) |
| `Item` is not `@Serializable`; the fixture is decoded into an internal DTO | `shared/src/commonMain/kotlin/bench/shared/` | B1, B2, B3, C (one module) | Swift export on Kotlin 2.4.x cannot compile kotlinx-serialization's API (KT-87791); the module stays the same bytes in every arm (research §1.11, D8, kept by the owner; B-23 tries 2.5.0 without it) |
| `navigation-compose` 2.9.2 (string routes, default transitions) | `compose-ui/build.gradle.kts` | C | the brief's "navigation inside CMP"; the wizard's shared-UI template has a single screen and no navigation, so this is the stack's idiomatic library added, at its newest stable release (B-10) |
| The thumbnails as Compose resources, from `apps/common/Thumbnails` (`customDirectory`) | same | C | Compose's own way to bundle an image; the SwiftUI arms bundle the same 50 files as plain bundle files, and each app carries them once (B-10) |
| One `const val BRIDGE` per bridge module | `bridge-*/src/commonMain/kotlin/bench/bridge/Bridge.kt` | B1, B2, B3 | a framework module with no source of its own is never linked (`NO-SOURCE`) |

Nothing else differs from the templates: `-O`, whole-module optimisation, dead-code stripping, the
static Kotlin framework and its release build are their defaults (research §1.9).
