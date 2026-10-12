---
id: B-31
title: "RQ1 on Apple's download estimate, with the encrypted worst case beside it (A2.4)"
status: wip
priority: P0
size: S
stage: stage-3-runs
blocked_by: [B-12]
---

# B-31 — RQ1, the download size again

B-12 read RQ1 on `zip -9` of an unencrypted archive. The owner pointed out that the App Store encrypts
the code after upload and encrypted bytes do not compress (amendment A2.4).

- **The decision and its reason.** Read RQ1 on Apple's own estimate of the download, App Thinning
  Size Report's `sizeCompressedApp` for the variant that serves the XS. Print beside it the worst case,
  with the executable's encrypted range made incompressible, and that case's verdict.
  `scripts/measure_download.py` builds each arm twice from a clean tree, signed, and exports it with
  thinning. Its control is B-12's: the size tools are in `make check` through
  `analysis/size_report_control.py`.
- Not covered: the real App Store figure. It needs a paid account.

- AC: `logs/b-31/download.csv` holds both builds of every arm, and `logs/b-31/report.md` is generated:
  per arm, Apple's download estimate, the install size, the worst case, and B-12's zip proxy for the
  same bytes. Two verdicts per comparison against A, one decisive and one printed beside it.
- Anchors: `scripts/measure_download.py`, `analysis/size_report.py`, `logs/b-31/`.
