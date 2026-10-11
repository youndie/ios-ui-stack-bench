# B-11 — visual parity on the iPhone XS

`xs/` is the output of `BENCH_DEVICE=1 DESTINATION=id=<udid> harness/parity.sh logs/b-11/xs`, run on
2026-10-11 with the phone in Light appearance. `xs/parity.md` and `xs/parity.csv` are
`analysis/parity_reader.py`'s reading of it, by the rule of BRIEF.md A1.6.

- `header.txt` — the commit, the Xcode build, the device and its iOS build, and the time; then the
  `sha256` of each arm's main executable as installed. The arms took turns on the phone, because a
  free account holds the runner and two of them.
- `<arm>.txt` — the `PARITY` geometry, in points, read from the accessibility tree.
- `<arm>.png` — the first screen, exported from the test result. `<arm>.attachments/` is the export
  itself, with its manifest.
- `<arm>.log` — the test's whole output. Its `PARITY_TREE` lines give every text and image frame of
  the first row, which is how C's layout was matched.

The test result bundles (`.xcresult`) are not committed: they are compressed binaries, and what they
hold is extracted above.

**No diff images are written.** A against B1, B2 and B3 differs in no pixel of the band, so their diff
would be empty. A against C differs by design (A1.6), and its share is published in `parity.md`.
