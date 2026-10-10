# BRIEF — what KMP and Compose Multiplatform cost an iOS app, measured on devices

> **Role of this document: what the study decided around its frozen pre-registration.** The
> questions, their green and red, the thresholds, the kill criteria and the methodology are
> [docs/research/source-brief.md](docs/research/source-brief.md) — the brief as received on
> 2026-10-10, byte for byte — and `make check` holds every byte of it. This file carries the record
> of that freeze, the pins, the answers to what the brief believed, and the amendments: appended,
> dated, with a reason; nothing is edited away.

<!-- frozen: path=docs/research/source-brief.md bytes=13229 sha256=3437dbc9ad7fa7fbc8a40009421e3900b75193924780f4fabf6dd091950f0aa3 scope=after-marker -->

**Owner:** Pavel (youndie) — decides amendments after the window and answers `question` items.
**Window:** open until the first measurement. It closes at the commit that adds the first file
under `logs/` other than its README ([B-01](docs/backlog/B-01-pins-and-the-amendment-window.md)),
and `make check` refuses a measurement that does not descend from the freeze.

## Pins

Resolved before the first measurement and not re-resolved afterwards. A version is pinned with the
build number or commit behind it, because a tag moves. Rows still open name the item that pins them.

| Row | Pin | Where it came from |
|---|---|---|
| Xcode | **open** — the released Xcode 27.0 is build `27A266a` (2026-09-14). The Mac holds only Xcode 27.0 beta 4 (`27A5228h`), which pins nothing | developer.apple.com/news/releases, 2026-10-10; `xcodebuild -version`. [B-01](docs/backlog/B-01-pins-and-the-amendment-window.md) |
| Kotlin | **open** — latest stable on 2026-10-10 is 2.4.21 (2026-10-08) | Maven Central `kotlin-gradle-plugin` metadata; JetBrains/kotlin releases. B-01 |
| Compose Multiplatform | **open** — latest stable on 2026-10-10 is 1.12.1 (2026-09-22); `1.13.0-alpha02` is a pre-release that Maven's `<release>` tag points at | Maven Central `org.jetbrains.compose.gradle.plugin` metadata; JetBrains/compose-multiplatform releases. B-01 |
| CMP `parallelRendering` | the framework default (`true` since 1.11.0), recorded because its default changed between versions | research §1.4 |
| Swift bridge for B and C | **open** — the owner's decision | [B-02](docs/backlog/B-02-swift-bridge.md) |
| Older device | **open** — candidate iPhone XS (`iPhone11,2`, A12, 4 GB, 60 Hz), iOS 18 at most | `xcrun devicectl list devices`; research §1.2. B-01 |
| Newer device | **open** — a 120 Hz ProMotion iPhone; the owner confirmed one will be available (2026-10-10) | B-01 |
| Bundle ids | **open** — fixed once and never changed (App IDs are capped at 10 per 7 days) | [B-04](docs/backlog/B-04-free-provisioning-probe.md) |
| Fixture and thumbnails | **open** — `sha256` of the generated JSON and of each PNG | [B-07](docs/backlog/B-07-fixture-and-shared-module.md) |
| Non-default flags | `docs/flags.md`, once a variant exists; proposed so far: `CADisableMinimumFrameDurationOnPhone = YES` in A and B (C's default) | research D3 |

## What was believed, answered

| Belief (from the brief) | Answered by | Answer |
|---|---|---|
| Free provisioning caps installed apps per device, "believed to be 3" | research §1.5 | **3**, Apple's membership comparison page. Whether the UI-test runner takes a slot: **unverified**, B-04 |
| Free provisioning profiles expire after 7 days | research §1.5 | **Yes**, same page; App IDs are also capped at 10 per 7 days |
| Animation Hitches may not see CMP's Metal-layer frames as it sees SwiftUI's | research §1.4 | Narrowed, not answered: CMP ≥ 1.11 presents through a `CATransaction`, so it *should* (H1). The injected stall decides, [B-06](docs/backlog/B-06-rq0-the-gate.md) |
| Free provisioning can run Release builds under Instruments | research §1.5 | **Unverified**: Xcode-installed builds carry `get-task-allow` in any configuration; nothing published for a Personal Team or for Animation Hitches and App Launch. B-04 |
| "A consistent signal is a 2–4× memory premium for CMP" | research §1.1 | **Not what the sources show**: 1.9× on a non-footprint metric (Zhuravko), ~6× full-screen on a simulator (Commencis), no native baseline (Software Mansion). RQ4's thresholds are a prior, not a summary |
| JetBrains' "~9 MB" is comparable to the `zip -9` proxy | research §1.1 | **Unknown**: the source does not say what it measured |
| The fairness flags (release, static, dead-code stripping, `-O`, WMO) are a configuration to apply | research §1.9 | They are the template's and the SDK's **defaults**; listed with sources, no tuning needed |

## Amendments

Made inside the window, before the first measurement. Each says what the pre-registration said,
what changes, the evidence that forced it, and whether it can move a verdict — and if it can only
move one towards green, what is published beside it. These are held by being appended and by review
of `git log -p BRIEF.md`; the script does not freeze them.

**None yet.** [research §2](docs/research/research-architecture.md) lists thirteen places where the
frozen text cannot be applied as written (I1–I13); [B-01](docs/backlog/B-01-pins-and-the-amendment-window.md)
settles each here, or records it as left as written, before the window closes. None of them asks for
a threshold to move.

## Amendment set 2 — after the window

Empty, and better left so. An amendment here is made by the owner, says that it is late, fixes an
incoherence rather than an inconvenient number, and is declared before the run it governs; it may
add evidence, never relax a threshold to meet a number. A budget extended by the owner is recorded
here too, with the elapsed days still reported.
