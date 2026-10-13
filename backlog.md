# Backlog: native SwiftUI vs KMP + SwiftUI vs KMP + Compose Multiplatform on iOS

> Role of this document: the study's work queue. **One file per item in
> [`docs/backlog/`](docs/backlog/)** — `B-NN-<slug>.md`. What lives here is the index (generated)
> and everything that is not an item: the goal, the stages, and the decisions.
>
> New item: copy [`docs/templates/backlog-item.md`](docs/templates/backlog-item.md), take the next
> free `B-NN`, then `make fix` and `make check`.

## Goal

Answer the brief's five questions — what KMP and Compose Multiplatform cost an iOS app in size,
startup, scroll smoothness and memory, against a native SwiftUI baseline, on physical iPhones — and
publish the answer whatever it turns out to be, negative results included. The pre-registration is
[docs/research/source-brief.md](docs/research/source-brief.md), frozen;
[BRIEF.md](BRIEF.md) carries its pins and amendments; the evidence that shaped this order is
[docs/research/research-architecture.md](docs/research/research-architecture.md).

This backlog is finished when [B-19](docs/backlog/B-19-write-up.md) closes — including when the
study is killed, because a stop is written up with the same care as a result.

**Build first, measure later** (amendment A1.3, owner, 2026-10-10). The brief put the gate first;
the owner moved the device work after development. The arms, the harness, the readers and the
analysis are built and checked on the simulator now; RQ0 ([B-06](docs/backlog/B-06-rq0-the-gate.md))
still gates every number, and no arm is measured before it is green on a device.

**What the loop takes, and what waits for the owner.** The loop works the items that need no
device: B-05, B-07–B-10, B-13–B-15, B-20–B-22, and — so that the devices find everything ready
(owner, 2026-10-11) — B-25 to B-29: the session runner, the size tooling, the parity tooling,
RQ0's control hooks, and parity reached on the simulator. The device items — [B-04](docs/backlog/B-04-free-provisioning-probe.md),
[B-06](docs/backlog/B-06-rq0-the-gate.md), [B-11](docs/backlog/B-11-parity-check.md)'s check on the
devices, [B-12](docs/backlog/B-12-rq1-size.md), [B-16](docs/backlog/B-16-dry-run-and-the-ruler.md)–[B-19](docs/backlog/B-19-write-up.md)
— and [B-01](docs/backlog/B-01-pins-and-the-amendment-window.md)'s close of the window wait for the
owner's go. B-12 needs no device but writes the first file under `logs/`, which closes the window.
[B-23](docs/backlog/B-23-kotlin-2-5-round.md) waits for Kotlin 2.5.0 to be stable and for the write-up.
[B-24](docs/backlog/B-24-xctrace-record-and-readers.md) — the Instruments recording and its readers — waits for
B-06's device traces: Instruments records no hitches on a simulator. Nothing here becomes a library, a JetBrains ticket or
an upstream fix: all three are non-goals of the brief, and an item proposing one does not belong in
this file.

## Stages

| Stage id | Stage | What it is |
|---|---|---|
| `stage-0-gate` | P0 — the gate | Pins, the owner's open decisions, the incoherences settled as amendments, what free provisioning allows, hello-world variants, RQ0. Kill criteria 1 and 2. |
| `stage-1-build` | P1 — build | The fixture and the shared module, the five arms (A, B1, B2, B3, C), visual parity. Kill criterion 3. |
| `stage-2-harness` | P2 — harness | Scenarios S1–S4, recording and readers, the analysis, the dry run with the ruler. Kill criterion 5; kill criterion 4's denominator. |
| `stage-3-runs` | P3 — runs | RQ1 from the builds; the full matrix on both devices. Kill criterion 4. |
| `stage-4-write-up` | P4 — write-up | One verdict per RQ, regenerated from the CSVs. |
| `stage-5-later` | After the study | Rounds the owner asked for that the main study does not answer. |

## Which item owns each kill criterion

| Kill criterion | Item |
|---|---|
| 1 — no device path | [B-04](docs/backlog/B-04-free-provisioning-probe.md) finds it first; [B-06](docs/backlog/B-06-rq0-the-gate.md) decides it |
| 2 — blind instrument | [B-06](docs/backlog/B-06-rq0-the-gate.md) |
| 3 — parity not reached in 5 working days | [B-11](docs/backlog/B-11-parity-check.md) |
| 4 — noise floor | measured in [B-16](docs/backlog/B-16-dry-run-and-the-ruler.md), applied in [B-17](docs/backlog/B-17-runs-on-the-older-device.md) and [B-18](docs/backlog/B-18-runs-on-the-newer-device.md) |
| 5 — measurement contamination | [B-16](docs/backlog/B-16-dry-run-and-the-ruler.md) |

## Decisions

- **2026-10-10 — the repository.** `ios-ui-stack-bench`, public, everything in English; layout of a
  measurement study (frozen brief, BRIEF.md, file-per-item backlog, `logs/`). Owner's answer to
  the brief's open decision "repository name and location".
- **2026-10-10 — the newer device will be available.** The owner confirmed a 120 Hz ProMotion
  iPhone for the "newer device" slot; its model is pinned in [B-01](docs/backlog/B-01-pins-and-the-amendment-window.md).
  The "older device" candidate on hand is an iPhone XS (A12, 4 GB, 60 Hz).

- **2026-10-10 — three Swift bridges, three B arms** ([B-02](docs/backlog/B-02-swift-bridge.md),
  amendment A1.1). B1 Objective-C export with a Swift adapter ([B-09](docs/backlog/B-09-variant-b.md)),
  B2 SKIE ([B-20](docs/backlog/B-20-variant-b2-skie.md)), B3 Swift export
  ([B-21](docs/backlog/B-21-variant-b3-swift-export.md)); C uses the Objective-C export and is paired
  with B1. RQ1's B − A and RQ5 get one verdict per arm and no best-of. Five apps under a cap of three
  make the session plan an amendment of [B-01](docs/backlog/B-01-pins-and-the-amendment-window.md).
- **2026-10-10 — build first, measure later** (amendment A1.3); **the loop merges its own pull
  requests** on a green head commit (owner) — see [CLAUDE.md](CLAUDE.md), "Pull requests".
- **2026-10-11 — amendment set A1.4; the devices come when the runs are ready** (owner). Every
  proposal of research §2 approved; Kotlin stays at 2.4.20 (2.5.0 kept in mind for Swift export,
  B-23). B-25 to B-28 prepare the device work.
- **2026-10-10 — D8 kept; a later round on Kotlin 2.5.0** (owner). The shared module keeps
  kotlinx-serialization internal for this study. B3 is to be tried again on Kotlin 2.5.0 without the
  workaround, as a round of its own, because SKIE does not support 2.5.0
  ([B-23](docs/backlog/B-23-kotlin-2-5-round.md)).
- **2026-10-10 — S3 stays descriptive** ([B-03](docs/backlog/B-03-filter-scenario-verdict.md),
  amendment A1.2).

## Marks

`[ ]` open · `[~]` in progress · `[x]` done · `[?]` open question · `[-]` dropped

<!-- BEGIN INDEX -->

## Open (3)

| Task | | Priority | Size | Blocked by |
|---|---|---|---|---|
| [B-18](docs/backlog/B-18-runs-on-the-newer-device.md) `[?]` | P3 — the full matrix on the newer device: S1–S4, every arm, rotated order | P1 | L | B-16 |
| [B-19](docs/backlog/B-19-write-up.md) `[ ]` | P4 — the write-up: one verdict per RQ, regenerated from the CSVs, negative results included | P1 | M | B-12, B-17, B-31 |
| [B-23](docs/backlog/B-23-kotlin-2-5-round.md) `[ ]` | A later round on Kotlin 2.5.0: arm B3 without D8, once Kotlin 2.5.0 is stable | P3 | M | - |

## Closed (28)

**P0 — the gate**

- [B-01](docs/backlog/B-01-pins-and-the-amendment-window.md) `[x]` - Pin the stand, settle the brief's incoherences as amendments, and close the window
- [B-02](docs/backlog/B-02-swift-bridge.md) `[x]` - Choose the Swift bridge for B and C: Objective-C export with an adapter, SKIE, or Swift export
- [B-03](docs/backlog/B-03-filter-scenario-verdict.md) `[x]` - Decide whether S3 (filter) gets its own green and red, or stays descriptive
- [B-04](docs/backlog/B-04-free-provisioning-probe.md) `[x]` - What free provisioning allows on the devices: apps per device, the test runner, Instruments on Release
- [B-05](docs/backlog/B-05-hello-world-variants.md) `[x]` - Hello-world arms A, B1, B2, B3 and C with the instrumentation the study will measure through
- [B-06](docs/backlog/B-06-rq0-the-gate.md) `[x]` - RQ0 — the gate: every metric captured on a device, the injected stall seen in every arm
- [B-28](docs/backlog/B-28-gate-control-hooks.md) `[x]` - The positive controls RQ0 needs: a known launch delay, a known dirty allocation, a known resource

**P1 — build**

- [B-07](docs/backlog/B-07-fixture-and-shared-module.md) `[x]` - The fixture and the shared Kotlin module: 2,000 items, 50 thumbnails, parse, filter, state
- [B-08](docs/backlog/B-08-variant-a.md) `[x]` - Variant A — Native: the full spec
- [B-09](docs/backlog/B-09-variant-b.md) `[x]` - Variant B1 — KMP + SwiftUI over the Objective-C export: the full spec
- [B-10](docs/backlog/B-10-variant-c.md) `[x]` - Variant C — KMP + CMP: the full spec
- [B-11](docs/backlog/B-11-parity-check.md) `[x]` - Visual parity before any measurement: item count, row height, first-screen diff
- [B-20](docs/backlog/B-20-variant-b2-skie.md) `[x]` - Variant B2 — KMP + SwiftUI over SKIE: the full spec
- [B-21](docs/backlog/B-21-variant-b3-swift-export.md) `[x]` - Variant B3 — KMP + SwiftUI over Swift export: the full spec, or the reason it cannot be built
- [B-22](docs/backlog/B-22-ci-builds-every-arm.md) `[x]` - CI builds every arm on macOS, so a green pull request means the apps still build
- [B-29](docs/backlog/B-29-parity-on-the-simulator.md) `[x]` - Bring the five arms to parity on the simulator, so B-11 on the devices confirms rather than builds

**P2 — harness**

- [B-13](docs/backlog/B-13-ui-test-scenarios.md) `[x]` - The UI-test scenarios S1–S4, one target driving every arm by bundle id
- [B-14](docs/backlog/B-14-trace-export-and-readers.md) `[x]` - xctrace record and export, and the readers that turn traces and in-app logs into CSVs
- [B-15](docs/backlog/B-15-analysis-and-intervals.md) `[x]` - The analysis: median and IQR per variant, bootstrap 95 % CIs, the verdict word per RQ
- [B-16](docs/backlog/B-16-dry-run-and-the-ruler.md) `[x]` - Dry run on one device: the ruler, the runner's and the instruments' own cost, thermal drift
- [B-24](docs/backlog/B-24-xctrace-record-and-readers.md) `[x]` - Record with xctrace beside every scenario, export its tables, and read them - on a device
- [B-25](docs/backlog/B-25-session-runner.md) `[x]` - One command per session: preflight, install, rotated runs, collection, runs.csv
- [B-26](docs/backlog/B-26-size-tooling.md) `[x]` - The size measurement as a script: unsigned arm64 archives, zip -9, link-map breakdown, determinism
- [B-27](docs/backlog/B-27-parity-tooling.md) `[x]` - Parity tooling: first-screen screenshots, geometry from the accessibility tree, list-region diff
- [B-30](docs/backlog/B-30-runner-free-scenarios.md) `[x]` - S2′ and S4′ without the runner: the app drives itself, the session records it (A2.2)

**P3 — runs**

- [B-12](docs/backlog/B-12-rq1-size.md) `[x]` - RQ1 — size: what KMP and CMP add to an arm64 app, uncompressed and zip -9, by component
- [B-17](docs/backlog/B-17-runs-on-the-older-device.md) `[x]` - P3 — the full matrix on the older device: S1–S4, every arm, rotated order
- [B-31](docs/backlog/B-31-rq1-download-size.md) `[x]` - RQ1 on Apple's download estimate, with the encrypted worst case beside it (A2.4)

<!-- END INDEX -->
