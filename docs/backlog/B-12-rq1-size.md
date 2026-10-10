---
id: B-12
title: "RQ1 — size: what KMP and CMP add to an arm64 app, uncompressed and zip -9, by component"
status: open
priority: P1
size: S
stage: stage-3-runs
blocked_by: [B-11]
---

# B-12 — RQ1, size

RQ1 as pre-registered: green if B − A ≤ 2 MB and C − A ≤ 12 MB on the compressed size proxy, red if
B − A > 5 MB or C − A > 20 MB. The proxy is an archive with signing disabled, arm64 `.app`:
uncompressed bytes, and `zip -9` as the download proxy.

Two facts change how the brief's cross-check is read ([research §1.9](../research/research-architecture.md)):
the Kotlin framework is linked **static** under the fairness rules, so the `.app` holds no Kotlin
framework or Skiko file to measure — they are inside the main executable; and the "~9 MB" the
green threshold is said to reproduce has to be compared with what JetBrains actually measured
([research §1.1](../research/research-architecture.md)).

- **The decision and its reason.** The per-component breakdown is taken from the linker map of
  the final link (`-Wl,-map,<file>`), summed by object-file origin: app code, Kotlin (stdlib,
  coroutines, serialization, the shared module), Skiko and Compose, Swift runtime shims. A map is
  a fact about the link; a guess from file sizes is not available once everything is in one binary.
- Size is deterministic, so there is no median: the variants are each built twice from a clean
  tree and the two main executables compared, so that "deterministic" is shown rather than assumed.
- Positive control: B-06's 1 MB incompressible resource, added and removed, moves the proxy by
  about 1 MB.

- AC: uncompressed and `zip -9` bytes per arm, B1 − A, B2 − A, B3 − A and C − A, a verdict word for
  each against the thresholds as written — three B verdicts, no combined one (amendment A1.1) — and the breakdown from the link maps — all regenerated from
  `logs/b-12/` by a script, never typed.
- AC: the two clean builds of each variant are byte-identical apart from the code signature, or
  the difference is recorded and its size stated.
- Anchors: `logs/b-12/`, `analysis/` (target).

---

## Noted before this item started — 2026-10-10 (B-10)

`scripts/build-arms.sh` printed a different digest for B3's merged static library
(`bridge-swift-export/build/MergedLibraries/.../libShared.a`) on two builds. Between those builds
B3's Kotlin and Swift sources did not change; only the Xcode projects did, through the generator. The
other arms' Kotlin binaries kept their digests. Either Swift export's output is not reproducible, or
it depends on something the projects changed. This is exactly what this item's "built twice from a
clean tree" acceptance is there to find, and it is recorded here so that item starts from it.
