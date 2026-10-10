---
id: B-11
title: "Visual parity before any measurement: item count, row height, first-screen diff"
status: open
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
