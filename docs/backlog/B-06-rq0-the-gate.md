---
id: B-06
title: "RQ0 — the gate: every metric captured on a device, the injected stall seen in every arm"
status: open
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
    both the App Launch trace and the in-app delta, within the run-to-run spread;
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
