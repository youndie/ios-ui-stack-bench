---
id: B-25
title: "One command per session: preflight, install, rotated runs, collection, runs.csv"
status: done
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

---

## Findings — 2026-10-11

**Done on the simulator; the device half (`xcrun devicectl` install and log pull) is written and runs
for the first time in B-04/B-06.**

- **`python3 harness/session.py <plan.json>`**:
  - installs the plan's arms at the start and records each installed main executable's sha256;
  - runs S1–S4 in batches, the arms rotated by run (A→B→C, B→C→A, C→A→B), each arm's first run of a
    scenario marked `counted=0`;
  - after every attempt, pulls that run's log, reads it and decides;
  - appends one row per attempt to `runs.csv`, and keeps every log with its CSVs under
    `<out>/<scenario>/<arm>/run-<n>-attempt-<k>/`.

  A run's log is the file that is new since the last pull, judged by name and not by the timestamp in
  it, because a device's clock is not the Mac's.
- **Preflight is read from the app's own log header**, which now carries the battery level next to
  Low Power Mode and the thermal state. The same rule therefore holds on a simulator and on a device:
  - **stop** the session on Low Power Mode, or on a device battery under 50 % or unknown;
  - **repeat** a run that the reader marked invalid, or whose thermal state left nominal at any point;
  - give up on a run after three attempts.

  The reader gained `battery`, `low_power`, `thermal_start` and `thermal_worst`, with a control case.
  The decision has its own control, `harness/session_control.py`, 8 cases in `make check`, rotation
  included. A simulator cannot be put in Low Power Mode or heated, so those refusals are shown on the
  decision function rather than live.
- **A reduced plan on the simulator** ran S1–S4 × 2 runs × all five arms: 40 attempts, 40 counted
  decisions, 20 warm-ups marked. The `runs.csv` it wrote is read by `analysis/verdicts.py` without
  edits, and every column the engine reads is present. Its device is `simulator`, so every verdict
  reads NOT MEASURED. **Simulator data cannot produce a verdict**, by construction. Simulator output is
  refused under `logs/`.
- Not covered here: the session plan under the install cap (A1.4 I5, B-04), and Instruments (B-24).
