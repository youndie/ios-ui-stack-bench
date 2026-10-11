---
id: B-27
title: "Parity tooling: first-screen screenshots, geometry from the accessibility tree, list-region diff"
status: wip
priority: P1
size: M
stage: stage-2-harness
blocked_by: [B-13]
---

# B-27 — Parity tooling

B-11 checks visual parity on the devices before any measurement, under A1.4's I12: geometry by
number (item count, row height, thumbnail and text sizes) and a pixel diff over the list content,
system chrome excluded, with a tolerance B-11 fixes before its first diff. The tooling for that
check needs no device and is built here, on the simulator.

- **The decision and its reason.** The geometry is read by the harness from the accessibility tree —
  each row's frame, the thumbnail's frame — so that "same row height in points" is a number from the
  running app, not an estimate from a screenshot. The pixel diff is a script over two screenshots of
  the same device, cropped to the list region the geometry names.
- Not covered: the tolerance (B-11 sets it) and the verdict on parity (B-11's, on the devices).

- AC: one command prints, per arm, the first screen's row count, row height, thumbnail size, and a
  screenshot path; on the simulator, for all five arms.
- AC: a diff script reports the share of differing pixels over the list region between two arms,
  and its control — an image against itself (0) and against a copy with a known patch changed — is
  in `make check`.
- AC: the simulator's numbers stay out of the repository; the commands do not.
- Anchors: `harness/`, `scripts/`.
