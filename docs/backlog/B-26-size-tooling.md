---
id: B-26
title: "The size measurement as a script: unsigned arm64 archives, zip -9, link-map breakdown, determinism"
status: done
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

---

## Findings — 2026-10-11

**Done.** The run's numbers stay in `build/`. They are RQ1's data, and RQ1 is measured by B-12 after
the window closes.

- **`python3 scripts/measure_size.py <out> [arms]`** archives each arm twice for the device SDK:
  Release, signing disabled, a new derived-data directory, the Kotlin build directories deleted, and
  Gradle's cache off. For each build it writes to `sizes.csv`:
  - uncompressed bytes and `zip -9 -r -X` bytes;
  - the main executable's size and sha256;
  - the link map summed by origin;
  - the section bytes and LINKEDIT bytes that explain the remainder.

  `analysis/verdicts.py` reads build 1. The script refuses `logs/` unless `BENCH_WINDOW_CLOSED=1` is
  set.
- **The breakdown** comes from `analysis/linkmap.py`, whose control `analysis/linkmap_control.py`
  (in `make check`) checks a hand-written map with zero-fill and dead-stripped symbols. The
  categories are:
  - app;
  - kotlin, the K/N program, `<Name>.framework.o`;
  - native-in-kotlin, every other member of the Kotlin framework: Skia, Skiko and Compose's UIKit
    glue in C;
  - swift-export;
  - linker, system and other.

  Symbols cover 99.8–100 % of every arm's section bytes. What they leave of the file is LINKEDIT,
  headers and page padding, which is a large share only of A's small executable. That is a property
  of Mach-O, not missing attribution, and the new columns show it.
- **Determinism** (research §1.13). A, B1 and B3 are byte-identical across two clean builds. B2 and C
  differ, at an identical size, inside the final link's `__objc_stubs`, `__stubs` and (C) `__text`,
  while C's Kotlin framework is identical. The difference is therefore the app link, not Kotlin. The
  proxy moves by tens of bytes against megabyte thresholds. The B3 move noted by B-10 is not
  reproduced.
  - **Corrected while it was being done:** a first section mapping read every differing byte as
    "outside sections" because it had parsed no sections at all. The mapping was redone before
    anything was concluded from it.
- **The 1 MiB control** (seeded random bytes added to a copy of each `.app`) moved `zip -9` by 1 MiB
  plus some 280 bytes of zip entry overhead, in every arm.
