# B-12 — RQ1, size

`sizes.csv` is `scripts/measure_size.py`'s output for two clean device archives (Release, arm64,
signing disabled) of every arm, built on 2026-10-11 with Xcode 27.0 (27A266a) from the commit B-12's
pull request starts from. Build 1 is the measurement; build 2 shows whether the build reproduces.
`report.md` is generated from it by `analysis/size_report.py` (command in
docs/backlog/B-12-rq1-size.md), never typed. `linkmaps/` holds build 1's final link map of each arm,
gzipped. The `map_*` columns of `sizes.csv` were computed at capture by the classifier B-12 then fixed
(see the item). The report's breakdown is computed from these maps.
