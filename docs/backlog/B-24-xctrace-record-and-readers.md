---
id: B-24
title: "Record with xctrace beside every scenario, export its tables, and read them - on a device"
status: done
priority: P1
size: M
stage: stage-2-harness
blocked_by: [B-06]
---

# B-24 — xctrace recording, export and readers, on a device

Split out of [B-14](B-14-trace-export-and-readers.md) on 2026-10-11. The brief's primary instruments
are Instruments templates: App Launch (startup), Animation Hitches (smoothness), Allocations /
VM Tracker (memory cross-check), CPU Profiler. **On the simulator, Animation Hitches records nothing**
("Hitches is not supported on this platform"), **and an App Launch recording hangs after its time
limit** (research §1.12). So no reader of their tables can be written against a real export until a
device has produced one, and a reader written against a guessed schema is exactly the reader that
silently drops rows.

- **The decision and its reason.** Wait for the first device traces — RQ0's ([B-06](B-06-rq0-the-gate.md))
  — then write each reader against the export it actually produced, with that export, cut down, as
  its control fixture.
- S1 is recorded by `xctrace record --template 'App Launch' --launch -- <bundle id>`, without the UI-test
  runner: xctrace can launch the app itself, and S1 then has no runner beside it at all.
- S2–S4 run under `xctrace record --all-processes` (or `--attach`, whichever the device accepts),
  started before the UI test and stopped after it; the trace's `sha256` goes into the log, and the
  bundle itself is not committed (`.gitignore`).

- AC: one command per session records, exports (`xctrace export --toc`, then the tables by xpath) and
  reads every scenario of every arm in the session's plan, writing the CSVs and the trace digests
  under `logs/b-NN/` with the header of [logs/README.md](../../logs/README.md).
- AC: a reader per table — App Launch intervals, hitches (with their durations), allocations / VM
  summary, CPU time — each with a control built from a real export of B-06, in `make check`, shown
  failing once on a broken reader.
- AC: the hitches reader and the in-app logger agree on B-06's injected stall in every arm, or the
  disagreement is written down (research §2, I4).
- Anchors: `harness/collect.sh`, `analysis/`, `logs/`.

---

## Done — 2026-10-11

**What the device allowed changed the plan.** No `xctrace` recording survives beside the UI-test
runner (B-06, A1.7). So the "one command per session" is `harness/session.py`, which works as
follows:
- **S1** is recorded by App Launch with Points of Interest, launched by `xctrace --launch` with no
  runner: wait 10 s, launch, record 10 s. `xctrace` ends the app when it stops, so every S1 starts
  from a process that is not running. The run's row in `runs.csv` carries `trace_process_to_list_ms`
  and `trace_process_to_first_frame_ms`. RQ2 and RQ5 read the first (`analysis/verdicts.py`
  `STARTUP`).
- **S2–S4** run through the harness, as before.
- **Once per arm at the session's end**, Animation Hitches and Activity Monitor record a
  self-scrolling launch. They go into `crosscheck.csv` beside the app's own figures of the same
  launch: hitch time ratio and longest hitch in the scrolling window, peak footprint, CPU time.
- **CPU** is the app's own `getrusage` time (`cpu_total_ms`), with Activity Monitor's CPU Time as
  its cross-check. That is late amendment A2.1, made by the owner after the window closed. CPU
  Profiler weighs its samples in cycles, not time.
- **Recording, export, hashing and clean-up** live in `harness/recording.py`, shared with RQ0's
  `harness/gate.py`. It deletes the bundles once they are hashed, and the raw `instruments*.ktrace`
  files that `xctrace` leaves in `$TMPDIR`.

**The readers** are in `analysis/xctrace_reader.py`: App Launch with Points of Interest, Animation
Hitches with the scrolling window, and Activity Monitor (footprint, CPU time). Their control is
`analysis/xctrace_reader_control.py`. It runs on B-06's real exports
(`analysis/fixtures/b-06/`), its expected values come from regular expressions over the raw XML, and
it is in `make check`. It caught three mutations of the reader. The agreement of the hitches reader
and the logger on the injected stall is B-06's table, in every arm.

**Checked on the XS** with a two-arm development session (A and C, scratchpad, not reported). Every
run was valid. S1's trace column was filled. Every cross-check recorded. On the same launch, Activity
Monitor and the app agree on peak footprint and CPU time. The first device run of `session.py` also
found a bug: a freshly installed app has no `Documents/bench` yet, so the first log pull failed. It
no longer does.
