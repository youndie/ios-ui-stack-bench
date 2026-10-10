---
id: B-25
title: "One command per session: preflight, install, rotated runs, collection, runs.csv"
status: open
priority: P1
size: M
stage: stage-2-harness
blocked_by: [B-14]
---

# B-25 — The session runner

The brief's P3 sessions are many hours of scripted runs: per device, five arms, 20 cold starts and 10
runs of S2–S4 each, the order rotated, the first run of each batch discarded, runs that leave nominal
thermal state repeated. Done by hand, a session is where an untracked mistake enters — a run
started on a hot device, a reinstall in the middle, a warm-up counted. So a session is one command,
written and dry-run before any device is attached ("when everything is ready for runs", owner,
2026-10-11).

- **The decision and its reason.** `harness/session.sh <plan>` reads a session plan — device, arms,
  scenarios, runs per scenario, rotation — and for each run calls the collector, then appends one
  row to `runs.csv` with `device`, `session`, `arm`, `scenario`, `run`, `counted` (0 for each batch's
  first run), the reader's `valid` and summary columns, and the thermal state at start and end. A run
  whose thermal state left nominal is repeated, and the repeat is logged beside the run it replaces.
- **Preflight refuses to start** unless the device is unlocked, battery above 50 %, Low Power Mode off,
  thermal state nominal, and the session's arms are installed and their main-executable digests
  recorded; on a simulator it only checks what a simulator has.
- The device half — install, launch, log pull through `xcrun devicectl` — is written here and run
  for the first time by B-04/B-06; on the simulator the same plan runs end to end.
- Not covered: Instruments (B-24), the session plan's arms under the install cap (A1.4, I5 — B-04).

- AC: a plan for the simulator runs every arm through S1–S4 with the protocol's rotation, and the
  resulting `runs.csv` feeds `analysis/verdicts.py` without hand edits (outside `logs/`: simulator
  numbers are never reported).
- AC: preflight refuses a run it should refuse — shown once for each condition it can check on the simulator.
- AC: a run the reader marks invalid is repeated, never counted, and the repeat is visible in the log.
- Anchors: `harness/`, `analysis/`.
