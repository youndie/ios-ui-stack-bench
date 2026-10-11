---
id: B-27
title: "Parity tooling: first-screen screenshots, geometry from the accessibility tree, list-region diff"
status: done
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

---

## Findings — 2026-10-11

**Done on the simulator**; B-11 runs the same commands on the devices.

- **`harness/parity.sh <out> [arms]`** runs `Parity.testFirstScreen` (`harness/HarnessUITests/Parity.swift`)
  against each arm. It prints `PARITY` lines from the accessibility tree: visible rows, the first
  row's height and top, the last visible row's bottom (clamped to the screen), the thumbnail size
  where it is exposed, the title's height and the screen scale. The screenshot is kept as a test
  attachment and exported with `xcresulttool`, so the same path works on a device, where `simctl`
  does not. It refuses `logs/` for simulator output.
- **`scripts/parity_diff.py`** gives the share of differing pixels between two screenshots over the
  band from the first row's top to the last row's bottom. That is the list content; the system chrome
  is outside (A1.4, I12). A channel difference above `--delta` counts as a difference. It decides
  nothing: B-11's tolerance does.
  - Standard library only, with its own PNG decoder: 8-bit RGB/RGBA, all five row filters, about 3 s
    for a 1206 × 2622 screenshot.
- **Control**: `scripts/parity_diff_control.py`, in `make check`, 6 cases.
  - The images are built and encoded with every row filter in turn, then decoded and compared pixel
    by pixel with their source.
  - An image against itself; a 5 % patch; a patch outside the band; a change under the delta.
  - **A mutant survived the first version.** A swapped Paeth predictor passed, because the control
    checked one row (not a Paeth row) and compared two decodes, which the same wrong decoder makes
    agree. Every row is now checked against the source, and the mutant fails.
- **Run on all five arms**, all give geometry and a screenshot. The Compose tree does not expose the
  thumbnail as an image. **The SwiftUI and the Compose rows do not have the same height yet.** Making
  them match is new item [B-29](B-29-parity-on-the-simulator.md), so that B-11 on the devices confirms
  parity rather than builds it. No simulator number is recorded here.
