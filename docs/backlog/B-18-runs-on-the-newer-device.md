---
id: B-18
title: "P3 — the full matrix on the newer device: S1–S4, every arm, rotated order"
status: question
priority: P1
size: L
stage: stage-3-runs
blocked_by: [B-16]
---

# B-18 — The full matrix on the newer device

The brief's P3 on the 120 Hz ProMotion device: 20 cold starts and 10 runs of each of S2–S4 per arm, the first run of
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
  the installed builds, under `logs/b-18/`.
- AC: the counted-run totals per variant × scenario match the protocol, with every discarded run
  listed and its reason.
- Anchors: `logs/b-18/`, `harness/` (target).

---

## Question — 2026-10-13

The owner reads every question on the iPhone XS (A1.7). The iPhone 17 Pro is measured later or not
at all. The tooling is ready for it: the harness ran S1 and S2 there in B-04, and every session is a
plan with a device id. Whether and when to run it is the owner's decision.
