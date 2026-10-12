# B-31 — RQ1 on Apple's download estimate (A2.4)

`download.csv` is `BENCH_WINDOW_CLOSED=1 python3 scripts/measure_download.py logs/b-31`, run on
2026-10-12 with Xcode 27.0 (27A266a): two clean, signed archives per arm, each exported as a
development build thinned for all variants. Build 1 is the measurement and build 2 the
reproducibility check. `report.md` is `python3 analysis/download_report.py logs/b-31/download.csv
--md logs/b-31/report.md`. `thinning/` keeps build 1's App Thinning Size Report and
`app-thinning.plist` of each arm, where `sizeCompressedApp` of the iPhone XS variant is read.
The archives and the exported IPAs are not kept.
