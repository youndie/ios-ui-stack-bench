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
| Xcode | **27.0, build `27A266a`** (released 2026-09-14), selected with `xcode-select`; iOS SDK `iphoneos27.0`. The beta (`27A5228h`) stays installed and builds nothing for this study | `xcodebuild -version` and `xcode-select -p` on the driving Mac, 2026-10-10; developer.apple.com/news/releases |
| Kotlin | **2.4.20**, tag `v2.4.20` at `890ac1d94fdb80eb85f0eeb5be5e4352df987b2f` — not the latest stable (2.4.21): SKIE 0.10.15 refuses 2.4.21 (A1.4, I14). 2.5.0 is B-23's round, for Swift export | `git ls-remote` JetBrains/kotlin, 2026-10-11; the SKIE build, research §1.11; owner, 2026-10-11 |
| Compose Multiplatform | **1.12.1**, tag `v1.12.1` at `bdd8e879b2fc4960934a99959d82400c96b7c590` (compose-multiplatform) and `a1a7f3533363aa93849541cf451af2363fc2070a` (compose-multiplatform-core); material3 1.12.0-alpha03 as the wizard's template carries it; navigation-compose 2.9.2 | `git ls-remote`, 2026-10-11; `gradle/libs.versions.toml` |
| CMP `parallelRendering` | the framework default (`true` since 1.11.0), recorded because its default changed between versions | research §1.4 |
| Swift bridges | **all three, one B arm each** (A1.1): B1 Objective-C export + Swift adapter, B2 **SKIE 0.10.15** (tag at `7e7b8b597a4da8ba121a33775799ad51e517beb5`, no configuration), B3 Swift export of Kotlin 2.4.20 with D8; C uses the Objective-C export | owner, 2026-10-10 ([B-02](docs/backlog/B-02-swift-bridge.md)); `git ls-remote` touchlab/SKIE, 2026-10-11 |
| Older device | **open** — candidate iPhone XS (`iPhone11,2`, A12, 4 GB, 60 Hz), iOS 18 at most | `xcrun devicectl list devices`; research §1.2. B-01 |
| Newer device | **open** — a 120 Hz ProMotion iPhone; the owner confirmed one will be available (2026-10-10) | B-01 |
| Bundle ids | `io.github.youndie.iosbench.{a,b1,b2,b3,c}`, and `.harness` for the UI-test runner — fixed, never changed (App IDs are capped at 10 per 7 days) | `apps/*/Configuration/Config.xcconfig`, `harness/generate_project.py` (B-05, B-13) |
| Fixture and thumbnails | `apps/common/Fixture/items.json`: 2,000 items, 1,058,836 bytes, sha256 `7a9693d18f2901f4c6ab12e962721fa5477e09affd56002e4141ce6431f98a3e`. The 50 thumbnails (400 × 400 px): sha256 `0dd4f22b2b893a1916641320a4032bce77b5f7e38b496edb4223192b0e1e7cda` over their per-file digests in name order. The filter test vector `fixtures/filter-vectors.json`: sha256 `d8d2e8327a164c1ee95836ce9f6b3ffdb3c0af1578d7e3d8e3df2118f1e11b78` | `fixtures/generate.py`, seed 20261010; `make check` holds every byte (`--check`), [B-07](docs/backlog/B-07-fixture-and-shared-module.md) |
| Non-default flags | [docs/flags.md](docs/flags.md) — `CADisableMinimumFrameDurationOnPhone` in A and B (D3, approved in A1.4), the bundle ids, Kotlin 2.4.20, D8, navigation-compose and Compose resources in C | B-05, B-10; owner, 2026-10-11 |

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

[Research §2](docs/research/research-architecture.md) lists fifteen places where the frozen text
cannot be applied as written (I1–I15); [B-01](docs/backlog/B-01-pins-and-the-amendment-window.md)
settles each here, or records it as left as written, before the window closes. None of them asks for
a threshold to move. The two below are the owner's answers to the brief's open decisions.

### A1.1 — B becomes three arms, one per Swift bridge (2026-10-10, owner, before the first measurement)

The pre-registration has one B — "Shared Kotlin module … same SwiftUI views as A" — with the bridge
an open decision, and its risk table says to "decide once and keep it identical in B and C". The
owner's decision on [B-02](docs/backlog/B-02-swift-bridge.md): **measure all three bridges.** B is
now B1 (Objective-C export with a hand-written Swift adapter), B2 (SKIE) and B3 (Swift export), each
its own app over the same compiled Kotlin module and the same SwiftUI views; C is built with the
Objective-C export, so B1→C is the brief's "cost of Compose UI" unchanged.

What it does to the verdicts: **no threshold moves.** RQ1's "B − A" and every RQ5 condition are
evaluated once per B arm against the thresholds as written, and published as three verdicts. **There
is no combined RQ5 verdict and no "best bridge" verdict** — three tries at one green would push RQ5
towards green by selection, which is the move an amendment may not make. RQ2, RQ3 and RQ4 concern C
and are unaffected.

What it does to the protocol: five apps against a free account's cap of three (research §1.5, I5),
so the brief's rotation inside a session becomes a set of sessions with A in every one of them; the
session plan is an amendment of B-01's, once B-04 has measured the cap. It also bounds the Kotlin pin
by SKIE's support (I14), and puts an Alpha toolchain in B3 (research Risk 8): a B3 that cannot carry
the spec is reported "not measured", with the failure.

### A1.2 — S3 (filter) stays descriptive (2026-10-10, owner, before the first measurement)

The brief's open decision "whether S3 (filter) gets its own red/green or stays descriptive"
([B-03](docs/backlog/B-03-filter-scenario-verdict.md)): **descriptive.** S3 is run and reported with
median and IQR per arm and per device, and no verdict word; nothing is added to the thresholds.

### A1.3 — build first, measure later (2026-10-10, owner, before the first measurement)

The pre-registration's phases put the gate first: "no variant is built in full until RQ0 is green on
a real device". The owner's decision: **develop first, run later** — the five arms, the harness and
the readers are built and checked on the simulator, and the device work (what free provisioning
allows, RQ0, parity on the device, every measurement) starts when the owner says so.

What it does to the verdicts: **nothing; no threshold moves, and RQ0 still gates every number** —
no arm is measured before RQ0 is green on a device. The simulator stays what the brief says it is:
"used only for development and … never reported". What it costs: if kill criterion 1 or 2 fires,
the build effort spent before it is lost, and the stop is written up with that effort counted; and
the protocol decisions B-04 informs (the session plan, I5) are made after the arms exist rather
than before — they change how the arms are installed and driven, not how they are built.

### A1.4 — the incoherences of research §2 settled as proposed (2026-10-11, owner, before the first measurement)

The owner approved every proposal of [research §2](docs/research/research-architecture.md), I1–I15,
and decisions D3 and D4, as written. **No threshold moves.** What each now means:

| # | Settled as |
|---|---|
| I1 | Kill criterion 4 is applied to each scenario at the counted runs it has: 19 for S1, 9 for each of S2–S4 (the first run of each batch is the warm-up) |
| I2 | A difference threshold (RQ2, RQ5) is held by the bootstrap interval of the median difference; RQ3's absolute thresholds by the interval of C's median; RQ4's ratio by the interval of the ratio of medians; "no single hitch ≥ 100 ms / ≥ 250 ms" by the maximum over the counted runs, with no interval; RQ1 is deterministic and compared as numbers. Green and red both need the median **and** the whole interval on their side (`analysis/verdicts.py`) |
| I3 | RQ4 and RQ5 are read on both devices; green only if green on both, red if red on either. RQ2 stays on the older device, RQ3 on both, as the brief says |
| I4 | The in-app logger's hitch time ratio is defined in `analysis/inapp_reader.py` (a missed vsync, inside S2's scroll windows, ms/s). If Animation Hitches cannot see C's frames (RQ0 grey), RQ3 is computed from the logger, and the write-up says so |
| I5 | Sessions share A as their anchor; B1 and C share a session; a comparison of two arms from different sessions is printed with A's figures from both. The exact session plan follows from the free-account cap that [B-04](docs/backlog/B-04-free-provisioning-probe.md) measures, and is appended here before the first session |
| I6 | Kill criterion 5's "overhead" is the shift in **the app's** figures with the UI-test runner attached against the app launched without it (B-16) |
| I7 | RQ4's growth is the footprint sample after the 50th exit from the detail screen minus the sample after the 5th |
| I8 | S1 is run as written and named a warm launch, in Apple's terms, in the write-up |
| I9 | The thresholds stand; the write-up does not claim to reproduce or refute JetBrains' 9 MB, whose metric is unstated |
| I10 | The thresholds stand; "Apple's bands" cites WWDC20 session 10077 |
| I11 | Nothing to amend; the write-up cites the sources, not the brief's Context |
| I12 | Parity is geometry by number (item count, row height, thumbnail and text sizes) plus a pixel diff over the list content, with the system chrome excluded; the tolerance number is fixed by [B-11](docs/backlog/B-11-parity-check.md) before its first diff and appended here |
| I13 | Pinned in the table above |
| I14 | Kotlin 2.4.20 for every Kotlin arm (above) |
| I15 | "MB" is 10^6 bytes |
| D3 | `CADisableMinimumFrameDurationOnPhone = YES` in every arm |
| D4 | Liquid Glass stays where the platform puts it; parity as in I12 |

Two rows are still to be completed inside the window, each by the item named: I5's session plan
(B-04) and I12's tolerance (B-11).

### A1.5 — the session plan (I5) and charging (2026-10-11, owner, before the first measurement)

[B-04](docs/backlog/B-04-free-provisioning-probe.md) measured the cap: three apps per device, and
the UI-test runner takes one of them, so **a session holds the runner and two arms**. A, B1 and C
cannot share one, as I5 assumed. The owner's choice, out of the options B-04 put to them:

- **Five sessions per device, each a pair:** {A, B1}, {A, B2}, {A, B3}, {A, C} and {B1, C}. Inside a
  session the two arms alternate in the brief's rotation (`harness/session.py`). Nothing is
  reinstalled mid-session; arms are swapped between sessions.
- **Every verdict reads one session.** RQ2–RQ4 read {A, C}. RQ5 for each B arm reads its {A, B}.
  The B1→C "cost of Compose UI" reads {B1, C}. A is measured in four sessions per device. Its
  figures from all four are printed side by side, so the drift between sessions is shown, not
  assumed away.
- **The phones stay on charge throughout every session.** Then a battery cannot run out partway
  through a session of about four hours. The cost is the heat of charging. It is the same for
  every arm in a session, and the write-up states it as a limitation. The stop rules stand: Low Power
  Mode, battery under 50 %, a thermal state above nominal.

**No threshold moves.** I5 is complete. One row is still open inside the window: I12's tolerance
(B-11).

## Amendment set 2 — after the window

Empty, and better left so. An amendment here is made by the owner, says that it is late, fixes an
incoherence rather than an inconvenient number, and is declared before the run it governs; it may
add evidence, never relax a threshold to meet a number. A budget extended by the owner is recorded
here too, with the elapsed days still reported.
