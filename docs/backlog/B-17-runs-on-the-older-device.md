---
id: B-17
title: "P3 — the full matrix on the older device: S1–S4, every arm, rotated order"
status: done
priority: P1
size: L
stage: stage-3-runs
blocked_by: [B-16]
---

# B-17 — The full matrix on the older device

The brief's P3 on the 60 Hz device with 4 GB or less: 20 cold starts and 10 runs of each of S2–S4 per arm, the first run of
each batch discarded as warm-up; the order rotated inside each session as the brief's A→B→C, B→C→A, C→A→B does, over the sessions of
the plan amended in [B-01](B-01-pins-and-the-amendment-window.md) — five arms do not fit one session
under the install cap, so A is in every session and is printed from each; runs whose
`thermalState` leaves nominal discarded and repeated. Before each session: reboot, Low Power Mode
off, battery above 50 %, airplane mode on, device cool to the touch; the session's arms reinstalled
at the start of the session, never in the middle of one.

- **The decision and its reason.** The session is one command ([B-14](B-14-trace-export-and-readers.md))
  and its log is captured as it runs; a run is repeated only for a rule written before it (thermal
  state, incomplete phase markers) and the repeat is logged beside the run it replaces.
- Kill criterion 4 is applied as amended in [B-01](B-01-pins-and-the-amendment-window.md): when a
  metric's within-variant spread is wider than the A–C gap it tests, that RQ closes inconclusive,
  and **no runs are added** to chase significance.
- Not covered: the verdicts. They are computed once, from the CSVs of both devices, in
  [B-19](B-19-write-up.md).

- AC: session logs with device model, iOS build, thermal state per run, battery, and the digests of
  the installed builds, under `logs/b-17/`.
- AC: the counted-run totals per variant × scenario match the protocol, with every discarded run
  listed and its reason.
- Anchors: `logs/b-17/`, `harness/` (target).

---

## Done — 2026-10-13

Three sessions on the iPhone XS replace the five pairs of the plan, by the owner's amendments A2.3
and A2.5. All three are under [logs/b-17/](../../logs/b-17/README.md). Each holds `runs.csv`,
`verdicts.txt` and `verdicts.csv` (`analysis/verdicts.py`), and every attempt's directory.

- **xs-1 {A, C}**, with the runner. Counted per arm: S1 19, S2p 9, S2 2, S3 9, S4p 9. One S2 run was
  repeated: the phone locked, the runner could not launch, and the run left no log.
- **xs-2 {A, B1, B2}**, no runner. Counted: S1 19 each, S2p 9 each, S4p 9 for A and 8 for B1 and B2.
  One S2p run was repeated: that launch started without its arguments. The owner stopped the session
  with two S4p runs left (B1, B2). No verdict reads S4p for a B arm. `runs.csv` was rebuilt from the
  attempt directories by `harness/session.py --rebuild`, and the session now writes it after every
  attempt.
- **xs-3 {A, B3, C}**, no runner. Counted: S1 19, S2p 9, S4p 9 per arm. Nothing was repeated.

**Verdicts** (A2.5: RQ2–RQ4 from xs-1, xs-3 printed beside as a repeat; RQ5 from each B arm's
session). They are regenerated into README.md by `analysis/readme_results.py`. RQ2 is green. RQ3 is red, read
beside A's own level on S2p. RQ4 is inconclusive on the peak, whose interval lies between 2× and 3×,
and green on growth. For every B arm, RQ5 is green on startup and footprint and inconclusive on the
hitch ratio, as B-16's ruler said it would be.

**Kill criterion 4**: no runs were added to any comparison.
