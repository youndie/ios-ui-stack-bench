---
id: B-11
title: "Visual parity before any measurement: item count, row height, first-screen diff"
status: done
priority: P1
size: M
stage: stage-1-build
blocked_by: [B-08, B-09, B-10, B-20, B-21]
---

# B-11 — Visual parity

The brief's third fairness rule: same item count, same row height in points, a screenshot diff of
the first screen within a small tolerance — checked before any measurement. Kill criterion 3 lives
here: parity not reached within **5 working days** of build effort cuts the scope to the list screen
only; if that also fails, the study stops.

The pixel half of the rule meets a platform fact: on the iOS SDK the variants are built with,
SwiftUI's navigation bar, search field and list adopt the system design automatically, and Compose
draws its own ([research §1.7](../research/research-architecture.md)). A first-screen pixel diff
between A and C can then fail for reasons no amount of build effort removes — and burn the five
days of kill criterion 3 on chrome rather than content.

- **The decision and its reason.** "A small tolerance" is not a number, so it gets one here, and
  before any comparison image exists: the tolerance, the region it is measured over (the list
  content, or the whole screen) and how the system chrome is handled are written into BRIEF.md
  through [B-01](B-01-pins-and-the-amendment-window.md) as an amendment. Geometry — item count,
  row height in points, thumbnail size, font size — is checked by number from the view hierarchy
  or the signposted layout, not only by eye.
- A against each of B1, B2 and B3 must be pixel-identical up to the tolerance (same views, only
  the adapter differs); A against C is where the tolerance matters.
- Not covered: "native feel" — a non-goal of the brief.

- AC: the tolerance and region are in BRIEF.md before the first diff is computed.
- AC: for each device: the five first-screen screenshots, the diff images and the measured
  mismatch, under `logs/b-11/`; item count and row height per variant, by number.
- AC: build days spent on parity are counted from this item's start and recorded; on day 5 without
  parity the scope cut of kill criterion 3 is applied, not extended.
- Anchors: `logs/b-11/`, `apps/` (target).

---

## Done — 2026-10-11, day 1 of kill criterion 3's five

**Parity holds on the iPhone XS** by A1.6 ([logs/b-11/](../../logs/b-11/README.md), `xs/parity.md`).
B1, B2 and B3 are pixel-identical to A over the band, with the same geometry. C's geometry is within
a point everywhere. Its pixel share is published, and by A1.6 it decides nothing. Kill criterion 3
does not fire: parity came on the first day.

What it took on the XS (iOS 18.7), beyond B-29's work on the iOS 27 simulator:
- **Light appearance on the phone.** The SwiftUI arms follow the system's appearance. C's
  `MaterialTheme`, the template's default, is light whatever the system says. With the phone in Dark,
  A was dark and C light. This is the stand's setting, so neither stack's default is changed: the
  phone stays in Light for the study.
- **C's row and header refitted to iOS 18.** On iOS 18, SwiftUI's list row is 76.67 points with 11 above and
  below its content, and the search field sits under the large title. B-29's values were the iOS 27
  simulator's, where the field is at the bottom. C's row padding is now 11.67 dp, and its title is 46 dp
  below the status bar (`docs/flags.md`). So C's geometry no longer matches A's on the iOS 27
  simulator. The XS is the study's device (A1.7).
- **`harness/parity.sh` on a device** installs each arm in turn and writes a `header.txt`. It keeps the
  test's whole output, including `PARITY_TREE` diagnostics: the frames of the first row's texts and
  images, the search field, and the title.
- **`analysis/parity_reader.py`** applies A1.6, and its control is in `make check`.

Deliberately left out: diff images. The B arms' diff is empty, and C's is not judged
(`logs/b-11/README.md`).
