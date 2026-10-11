---
id: B-06
title: "RQ0 — the gate: every metric captured on a device, the injected stall seen in every arm"
status: done
priority: P0
size: M
stage: stage-0-gate
blocked_by: [B-01, B-05]
---

# B-06 — RQ0, the gate

RQ0 as pre-registered: all three variants install as Release builds via free provisioning;
`xctrace` records App Launch, Animation Hitches and memory footprint for each; an injected 50 ms
main-thread stall shows up as a hitch in all three, in both the Instruments trace and the in-app
frame logger. It owns kill criteria 1 (no device path) and 2 (blind instrument). Output: `GATE.md`
with the verdict per metric. Since amendment A1.1 "all three" reads as every arm — A, B1, B2, B3
and C — because an arm the gate never saw has no instrument anybody showed working.

The risk the brief names is real and specific: C presents its frames from a Metal layer of its own,
and whether Instruments' hitch accounting sees those frames the way it sees Core Animation commits
is not documented ([research §1.4](../research/research-architecture.md)). The injected stall is the
positive control that answers it.

- **The decision and its reason.** Each metric gets a positive control, not only smoothness: a
  measurement that cannot see a known effect produces exactly the evidence of one that saw nothing
  to measure.
  - smoothness — the 50 ms stall, in every arm, on both devices (the brief's own control);
    plus a stall of 0 ms through the same code path, which must **not** register;
  - startup — a known delay (200 ms) inserted before "list populated" must come out as +200 ms in
    both the App Launch trace and the in-app delta, within the run-to-run spread — read at the
    median of repeated runs, because a single pair of runs cannot show it (B-28);
  - memory — a known allocation (50 MB, written so the pages are dirty) must raise the sampled
    `phys_footprint` by about that much and show in the Allocations / VM Tracker trace;
  - size — a known incompressible resource (1 MB of random bytes) must raise the compressed size
    proxy by about 1 MB.
- If the stall is visible to one instrument and not the other for C, RQ0 is **grey**, not green,
  and what RQ3 is computed from is decided in B-01 before the window closes
  ([research §2](../research/research-architecture.md), I4).
- Not covered: any comparison of variants. One recording per metric per variant, and nothing in
  this item is a result about A, B or C.

- AC: `GATE.md` (target) has one row per metric × variant × device: captured or not, the control's
  expected and observed value, the log path.
- AC: every row's raw output is under `logs/b-06/`, with the header of [logs/README.md](../../logs/README.md).
- AC: if kill criterion 1 or 2 fires, the stop is written up in GATE.md with the obstacles in the
  order they were hit, and the backlog is closed accordingly — simulator numbers are not a substitute.
- Anchors: `logs/b-06/`, `GATE.md` (target), `instrumentation/` (target).

---

## Iteration 1 — 2026-10-11

**What the gate became, and why** (amendment A1.7, owner):
- **The XS only.** The owner reads every question on the iPhone XS. The 17 Pro comes later or not at
  all, so "both devices" in the AC above reads "the XS".
- **Animation Hitches cannot record beside the UI-test runner on a device.** On the XS, a recording
  started before or during S2 ended within a second, "Device disconnected", in three tries of four;
  the test passed. The smoothness control therefore runs twice. Once on a run where the app scrolls
  its own list (`-benchAutoScroll`, a new hook absent from every measured run), launched by `xctrace
  --launch`: both instruments see the same stalls there. And once on S2 through the harness, for the
  logger RQ3 is computed from.
- **App Launch records no signposts** unless the Points of Interest instrument is added. With it,
  "list populated" is in the trace for every arm, including C, where the first frame comes before
  the list.
- **Allocations exports none of its data**, so memory's Instruments figure is Activity Monitor's
  `memory-physical-footprint` of the app's process.
- **The log writer could kill the app.** `FileHandle.write(_:)` raises an Objective-C exception on a
  failed write. On the XS a full disk did exactly that mid-S2. It now uses `write(contentsOf:)`,
  records a `writeError` line, and the reader marks such a run invalid (a new control case).
  The owner freed space on the phone.

**Probes before the gate** (scratchpad, not reported): on the XS, Animation Hitches shows the 50 ms
stall as ~50 ms "Pre-Commit latency" hitches in A and in C on the self-scrolling run, and nothing at
0 ms. So research §1.4's open question, whether Hitches sees CMP's Metal-layer frames, leans "yes"
before the gate's own rows.

**The pass conditions** are fixed in `analysis/gate_reader.py`'s header and committed before the
first recording under `logs/b-06/`: the stall seen by the logger at ≥ 90 % (and ≤ 5 % at 0 ms), by
Hitches at least once in the scrolling window (and nothing ≥ 40 ms at 0 ms), startup +150 to +250 ms
at the median of 5 vs 5, memory +40 to +60 MiB at the median of 3 vs 3, size +0.95 to +1.10 MiB.

## Result — 2026-10-11

The gate ran on the XS for all five arms, from commit `e3ab58f`, into
[logs/b-06/](../../logs/b-06/README.md); [GATE.md](../../GATE.md) has the generated table and its
reading. **RQ0 is not green under its own rule, by one row of 55**: B1's in-app startup control came
out just above its 250 ms ceiling, while App Launch, the instrument startup is read from (A1.7),
passes for B1 and every other arm. The ceiling is not moved. The stall is seen by both instruments in
every arm, C included, so H1 holds on the XS. Kill criteria 1 and 2 do not fire. That commit closed
the amendment window, and BRIEF.md names it.

Found on the way, for the items that use these tools:
- **xctrace leaves its raw kernel traces behind.** The Mac's temporary folder held about 29 GB of
  `instruments*.ktrace` after the dry run and half the gate, and a full disk killed the first gate
  run. Only `logs/b-06` was lost, and it was rerun from scratch. A session command has to delete them
  after each recording ([B-24](B-24-xctrace-record-and-readers.md)). The phone's disk matters as
  well: the XS filled up during a recording.
- **xctrace needs the phone unlocked.** A locked XS fails the runner with "Timed out while enabling
  automation mode".
- **C's S2 run is shorter** than the SwiftUI arms' runs: its log holds fewer one-second stall ticks
  for the same 40 flings. RQ3 divides by the scroll windows' length, so its ratio is unaffected. The
  difference itself is B-17's to look at, not this item's.
- **The trace readers exist now.** `analysis/gate_reader.py` reads Animation Hitches, App Launch with
  Points of Interest, and Activity Monitor, with a control built from real exports. B-24 reuses them
  for the sessions, rather than writing them anew.
