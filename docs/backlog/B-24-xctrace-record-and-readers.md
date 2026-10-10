---
id: B-24
title: "Record with xctrace beside every scenario, export its tables, and read them - on a device"
status: open
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
