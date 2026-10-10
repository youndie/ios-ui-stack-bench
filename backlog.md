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

**The gate comes first.** No variant is built in full until RQ0 is green on a real device
([B-06](docs/backlog/B-06-rq0-the-gate.md)). Nothing here becomes a library, a JetBrains ticket or
an upstream fix: all three are non-goals of the brief, and an item proposing one does not belong in
this file.

## Stages

| Stage id | Stage | What it is |
|---|---|---|
| `stage-0-gate` | P0 — the gate | Pins, the owner's open decisions, the incoherences settled as amendments, what free provisioning allows, hello-world variants, RQ0. Kill criteria 1 and 2. |
| `stage-1-build` | P1 — build | The fixture and the shared module, the three variants, visual parity. Kill criterion 3. |
| `stage-2-harness` | P2 — harness | Scenarios S1–S4, recording and readers, the analysis, the dry run with the ruler. Kill criterion 5; kill criterion 4's denominator. |
| `stage-3-runs` | P3 — runs | RQ1 from the builds; the full matrix on both devices. Kill criterion 4. |
| `stage-4-write-up` | P4 — write-up | One verdict per RQ, regenerated from the CSVs. |

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

## Marks

`[ ]` open · `[~]` in progress · `[x]` done · `[?]` open question · `[-]` dropped

<!-- BEGIN INDEX -->

## Open (19)

| Task | | Priority | Size | Blocked by |
|---|---|---|---|---|
| [B-01](docs/backlog/B-01-pins-and-the-amendment-window.md) `[ ]` | Pin the stand, settle the brief's incoherences as amendments, and close the window | P0 | S | B-02, B-03, B-04 |
| [B-02](docs/backlog/B-02-swift-bridge.md) `[?]` | Choose the Swift bridge for B and C: Objective-C export with an adapter, SKIE, or Swift export | P0 | XS | - |
| [B-04](docs/backlog/B-04-free-provisioning-probe.md) `[ ]` | What free provisioning allows on the devices: apps per device, the test runner, Instruments on Release | P0 | S | - |
| [B-05](docs/backlog/B-05-hello-world-variants.md) `[ ]` | Hello-world A, B and C with the instrumentation the study will measure through | P0 | M | B-02, B-04 |
| [B-06](docs/backlog/B-06-rq0-the-gate.md) `[ ]` | RQ0 — the gate: every metric captured on a device, the injected stall seen in all three | P0 | M | B-01, B-05 |
| [B-03](docs/backlog/B-03-filter-scenario-verdict.md) `[?]` | Decide whether S3 (filter) gets its own green and red, or stays descriptive | P1 | XS | - |
| [B-07](docs/backlog/B-07-fixture-and-shared-module.md) `[ ]` | The fixture and the shared Kotlin module: 2,000 items, 50 thumbnails, parse, filter, state | P1 | M | B-06 |
| [B-08](docs/backlog/B-08-variant-a.md) `[ ]` | Variant A — Native: the full spec | P1 | M | B-07 |
| [B-09](docs/backlog/B-09-variant-b.md) `[ ]` | Variant B — KMP + SwiftUI: the full spec | P1 | M | B-07 |
| [B-10](docs/backlog/B-10-variant-c.md) `[ ]` | Variant C — KMP + CMP: the full spec | P1 | M | B-07 |
| [B-11](docs/backlog/B-11-parity-check.md) `[ ]` | Visual parity before any measurement: item count, row height, first-screen diff | P1 | M | B-08, B-09, B-10 |
| [B-12](docs/backlog/B-12-rq1-size.md) `[ ]` | RQ1 — size: what KMP and CMP add to an arm64 app, uncompressed and zip -9, by component | P1 | S | B-11 |
| [B-13](docs/backlog/B-13-ui-test-scenarios.md) `[ ]` | The UI-test scenarios S1–S4, one target driving all three variants by bundle id | P1 | M | B-11 |
| [B-14](docs/backlog/B-14-trace-export-and-readers.md) `[ ]` | xctrace record and export, and the readers that turn traces and in-app logs into CSVs | P1 | M | B-13 |
| [B-15](docs/backlog/B-15-analysis-and-intervals.md) `[ ]` | The analysis: median and IQR per variant, bootstrap 95 % CIs, the verdict word per RQ | P1 | M | B-14 |
| [B-16](docs/backlog/B-16-dry-run-and-the-ruler.md) `[ ]` | Dry run on one device: the ruler, the runner's and the instruments' own cost, thermal drift | P1 | M | B-15 |
| [B-17](docs/backlog/B-17-runs-on-the-older-device.md) `[ ]` | P3 — the full matrix on the older device: S1–S4, three variants, rotated order | P1 | L | B-16 |
| [B-18](docs/backlog/B-18-runs-on-the-newer-device.md) `[ ]` | P3 — the full matrix on the newer device: S1–S4, three variants, rotated order | P1 | L | B-16 |
| [B-19](docs/backlog/B-19-write-up.md) `[ ]` | P4 — the write-up: one verdict per RQ, regenerated from the CSVs, negative results included | P1 | M | B-12, B-17, B-18 |

## Closed (0)

<!-- END INDEX -->
