# ios-ui-stack-bench

One iOS app built five times — native SwiftUI, Kotlin Multiplatform with SwiftUI views over three
different Swift bridges, and Kotlin Multiplatform with Compose Multiplatform — and measured on
physical iPhones for size, startup, scroll smoothness and memory. The methodology and the raw data sit next to every number.

**Status: measuring on the iPhone XS.** The questions, their thresholds and the kill criteria were
fixed before any code and are held byte for byte by `make check`. The window for amending them
closed with the first measurement, on 2026-10-11. The changes made after it are marked late in
[BRIEF.md](BRIEF.md). The five arms are built, the instruments passed their gate, and the first of
three sessions ({A, C}) is done; {A, B1, B2} and {A, B3, C} follow (A2.5). The results below are verdicts so far, not the write-up.

| Variant | Logic | UI |
|---|---|---|
| A — Native | Swift | SwiftUI |
| B1 / B2 / B3 — KMP + SwiftUI | shared Kotlin module, bridged by the Objective-C export, SKIE, or Swift export | the same SwiftUI views as A |
| C — KMP + CMP | the same shared Kotlin module as B | Compose Multiplatform |

A→B isolates the Kotlin/Native runtime and the Swift bridge — three bridges, one arm each; B1→C
isolates the Compose renderer and runtime.

## Results so far

<!-- BEGIN RESULTS (analysis/readme_results.py) -->

Read on the iPhone XS only (BRIEF.md A1.7); every figure is regenerated from `logs/` by `analysis/readme_results.py`. A verdict is green or red only when the median and its whole 95 % interval are on that side of the line; otherwise it is inconclusive.

| Question | Verdict | Figure | Raw data |
|---|---|---|---|
| RQ0 — every metric capturable, the injected stall seen | not green | 54 of 55 control rows pass; the stall is seen by both instruments in every arm, C included. Not passing: B1 startup +200 ms (in-app log) observed +252 ms against 150-250 ms | [GATE.md](GATE.md) |
| RQ1 — download size, B1 − A | green | +0.74 MB on Apple's estimate (green <= 2 MB); encrypted worst case +1.85 MB, green | [logs/b-31](logs/b-31/report.md) |
| RQ1 — download size, B2 − A | green | +0.80 MB on Apple's estimate (green <= 2 MB); encrypted worst case +2.03 MB, inconclusive | [logs/b-31](logs/b-31/report.md) |
| RQ1 — download size, B3 − A | green | +0.77 MB on Apple's estimate (green <= 2 MB); encrypted worst case +1.93 MB, green | [logs/b-31](logs/b-31/report.md) |
| RQ1 — download size, C − A | green | +10.30 MB on Apple's estimate (green <= 12 MB); encrypted worst case +26.57 MB, red | [logs/b-31](logs/b-31/report.md) |
| RQ2 — startup, C − A | green | +56 ms (95 % interval 34 to 74); green <= +100 ms, red > +250 ms | [logs/b-17/xs-1](logs/b-17/xs-1/verdicts.txt) |
| RQ3 — hitch time, C | red | 20.2 ms/s (95 % interval 17.5 to 20.9); green < 5 ms/s, red > 10 ms/s | [logs/b-17/xs-1](logs/b-17/xs-1/verdicts.txt) |
| RQ3 — longest hitch, C | green | 33 ms; green < 100 ms, red >= 250 ms | [logs/b-17/xs-1](logs/b-17/xs-1/verdicts.txt) |
| RQ4 — footprint growth over 50 cycles, C | green | -1.3 MB (95 % interval -2.3 to 0.7); green < 5 MB, red >= 20 MB | [logs/b-17/xs-1](logs/b-17/xs-1/verdicts.txt) |
| RQ4 — peak footprint, C / A | inconclusive | 2.51× (95 % interval 2.46–2.59); green <= 2x, red > 3x | [logs/b-17/xs-1](logs/b-17/xs-1/verdicts.txt) |
| RQ5 — peak footprint, B1 − A | green | +6.2 MB (95 % interval +3.7 to +9.2); green <= +20 MB, red > +50 MB | [logs/b-17/xs-2](logs/b-17/xs-2/verdicts.txt) |
| RQ5 — hitch time, B1 − A | inconclusive | +0.4 ms/s (95 % interval -1.1 to 1.3); green <= +1 ms/s, red > +2 ms/s | [logs/b-17/xs-2](logs/b-17/xs-2/verdicts.txt) |
| RQ5 — startup, B1 − A | green | +7 ms (95 % interval 0 to 21); green <= +50 ms, red > +150 ms | [logs/b-17/xs-2](logs/b-17/xs-2/verdicts.txt) |
| RQ5 — peak footprint, B2 − A | green | +6.7 MB (95 % interval +3.7 to +9.6); green <= +20 MB, red > +50 MB | [logs/b-17/xs-2](logs/b-17/xs-2/verdicts.txt) |
| RQ5 — hitch time, B2 − A | inconclusive | +1.6 ms/s (95 % interval -0.5 to 2.5); green <= +1 ms/s, red > +2 ms/s | [logs/b-17/xs-2](logs/b-17/xs-2/verdicts.txt) |
| RQ5 — startup, B2 − A | green | +13 ms (95 % interval 5 to 30); green <= +50 ms, red > +150 ms | [logs/b-17/xs-2](logs/b-17/xs-2/verdicts.txt) |

RQ3's bars are absolute, and on this phone the native list itself is not under them: A's own hitch time on the same self-scrolling run is 15.2 ms/s (median), so C's red is read beside A's level. The scroll is driven by the app itself, not by a finger (A2.2); on real flings through the UI-test runner the frame logger shows the same direction.


<!-- END RESULTS -->

## Where to read

- [docs/research/source-brief.md](docs/research/source-brief.md) — the brief as received, frozen:
  research questions, thresholds, methodology, kill criteria, non-goals.
- [BRIEF.md](BRIEF.md) — what the study decided around it: pins, answers to what the brief
  believed, amendments made before the first measurement.
- [docs/research/research-architecture.md](docs/research/research-architecture.md) — the evidence
  the study starts from: prior work as its sources actually report it, the stand, and the premises
  of the brief that did not survive checking.
- [backlog.md](backlog.md) — the work queue, one file per item in [docs/backlog/](docs/backlog/).
- [logs/](logs/) — every raw run and recording, by backlog item.

## Checks

```bash
pip install pyyaml
make check
```

The documentation checks ([docs-bootstrap](https://github.com/youndie/docs-bootstrap)) and the
freeze of the pre-registration. CI runs exactly the same target, and builds every arm on macOS with
the pinned Xcode:

```bash
scripts/build-arms.sh
```

## License

MIT — see [LICENSE](LICENSE).
