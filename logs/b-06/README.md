# B-06 — RQ0, the gate, on the iPhone XS

`xs/<arm>/` holds what `harness/gate.py` recorded for one arm on 2026-10-11, and `xs/gate.csv` what
`analysis/gate_reader.py` read out of it. [GATE.md](../../GATE.md) has the same table, and the
pass conditions are in `analysis/gate_reader.py`'s header, committed before the first recording.

Per arm:
- `header.json` — the device (model, `hw.machine`, iOS and build), the Xcode and `xctrace` versions,
  the commit the arm was built from, its bundle id, and the `sha256` of its main executable.
- `smooth-autoscroll/stall-50`, `stall-0` — Animation Hitches with Points of Interest, the app
  scrolling its own list, with the stall injector at 50 ms and at 0 ms.
- `smooth-s2/stall-50`, `stall-0` — S2 through the harness with the same two stalls: `test.log` and
  the app's log.
- `startup/delay-200-<i>`, `delay-0-<i>` — App Launch with Points of Interest, 5 launches each,
  interleaved.
- `memory/alloc-50-<i>`, `alloc-0-<i>` — Activity Monitor, 3 launches each, interleaved.
- `size/size.json` — the zip proxy's growth when 1 MiB of seeded random bytes is added to the
  device build.

Each recording keeps the tables it is read through, exported by `xctrace export` verbatim
(`*.xml`), the `sha256` of its trace bundle (`trace.sha256`; the bundles are not kept), the
`xctrace` command and its output (`xctrace.log`), and the app's own log of that launch
(`app.ndjson`, whose header line carries the battery, Low Power Mode and thermal state). No
recording failed, so there is no `attempt-<k>` directory.

These are controls, not measurements of the arms. Nothing here compares A, B and C, and no figure
in it is a result about any of them.
