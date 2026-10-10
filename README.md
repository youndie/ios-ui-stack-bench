# ios-ui-stack-bench

One iOS app built three times — native SwiftUI, Kotlin Multiplatform with SwiftUI views, and Kotlin
Multiplatform with Compose Multiplatform — and measured on physical iPhones for size, startup,
scroll smoothness and memory. The methodology and the raw data sit next to every number.

**Status: pre-registration.** No app exists yet and nothing has been measured. The questions, their
green and red thresholds and the kill criteria were fixed before any code, and `make check` holds
them byte for byte; nothing in this repository is a result until the results document says so.

| Variant | Logic | UI |
|---|---|---|
| A — Native | Swift | SwiftUI |
| B — KMP + SwiftUI | shared Kotlin module | the same SwiftUI views as A |
| C — KMP + CMP | the same shared Kotlin module as B | Compose Multiplatform |

A→B isolates the Kotlin/Native runtime and the Swift bridge; B→C isolates the Compose renderer and
runtime.

## Where to read

- [docs/research/source-brief.md](docs/research/source-brief.md) — the brief as received, frozen:
  research questions, thresholds, methodology, kill criteria, non-goals.
- [BRIEF.md](BRIEF.md) — what the study decided around it: pins, answers to what the brief
  believed, amendments made before the first measurement.
- [docs/research/research-architecture.md](docs/research/research-architecture.md) — the evidence
  the study starts from: prior work as its sources actually report it, the stand, and the premises
  of the brief that did not survive checking.
- [backlog.md](backlog.md) — the work queue, one file per item in [docs/backlog/](docs/backlog/).
- [logs/](logs/) — raw runs, once there are any.

## Checks

```bash
pip install pyyaml
make check
```

The documentation checks ([docs-bootstrap](https://github.com/youndie/docs-bootstrap)) and the
freeze of the pre-registration. CI runs exactly the same target.

## License

MIT — see [LICENSE](LICENSE).
