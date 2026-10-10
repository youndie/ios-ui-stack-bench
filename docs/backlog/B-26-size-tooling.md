---
id: B-26
title: "The size measurement as a script: unsigned arm64 archives, zip -9, link-map breakdown, determinism"
status: open
priority: P1
size: M
stage: stage-2-harness
blocked_by: [B-21]
---

# B-26 — The size measurement, ready before it counts

RQ1 needs no device: the brief's proxy is an archive with signing disabled, the arm64 `.app`,
uncompressed and `zip -9`, with a per-component breakdown ([B-12](B-12-rq1-size.md)). But B-12
writes the first file under `logs/` and so closes the amendment window; it waits for the owner's go.
Everything up to that write is built here, run into `build/`, and checked.

- **The decision and its reason.** `scripts/measure-size.sh` archives each arm for the device SDK
  (Release, `CODE_SIGNING_ALLOWED=NO`), records the `.app`'s uncompressed bytes and its `zip -9` size,
  and sums the final link map (`LD_GENERATE_MAP_FILE`, research D6) by object origin: app, Kotlin
  (shared module, coroutines, serialization, stdlib), Skiko and Compose, Swift runtime. It writes
  `sizes.csv` in the shape `analysis/verdicts.py` reads.
- **Determinism is checked, not assumed.** Every arm is built twice from a clean tree and the two
  main executables compared. B3's Kotlin binary already moved once between builds with unchanged
  sources (B-12's note); this item finds out why, or records that it is so.
- Positive control: an extra incompressible 1 MB resource moves the proxy by about 1 MB.

- AC: the script runs for all five arms into `build/`, and its `sizes.csv` feeds `analysis/verdicts.py`.
- AC: the link-map breakdown sums to the main executable's size within a stated remainder.
- AC: the two clean builds of each arm agree byte for byte apart from what is named and explained.
- AC: the 1 MB control moves the compressed proxy by about 1 MB.
- Anchors: `scripts/`, `apps/generate_projects.py`.
