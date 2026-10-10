# Raw logs

One directory per backlog item, `logs/b-NN/`, each holding the raw output of the runs that item
produced and a `README.md` saying what to read it for.

**These are the deliverable, not an appendix.** Every figure in a document has a path into here,
and a figure without one does not go into a document. A retraction is appended to the file that
carried the original; the original is not edited away.

What goes here, per run:

- the exported CSVs of every `xctrace` recording (`xctrace export`), and the in-app logs (signpost
  deltas, `CADisplayLink` frame intervals, `phys_footprint` samples, `thermalState`);
- the `sha256` of every `.trace` bundle the CSVs were exported from. The bundles themselves are
  large and are not committed (`.gitignore`); the hash ties each CSV to the recording it came from;
- a header on every log: device model and `hw.machine`, iOS version and build, Xcode and `xctrace`
  versions, the variant's bundle id, its build's commit and the `sha256` of its main executable,
  battery level, Low Power Mode, thermal state at start and end.

**Only measurements of the arms go here.** The first file under `logs/` closes the amendment window,
so what is not a measurement lives elsewhere: probes of the stand — what free provisioning allows,
whether an instrument records at all — under `stand/b-NN/`, and anything from the simulator in the
pull request that used it, never in this repository's data (the brief: simulator results "are never
reported").

Logs are captured on the Mac that drives the device, by the command that runs the session, and are
not edited after capture. The first file added here closes the amendment window of
[BRIEF.md](../BRIEF.md): `make check` refuses a measurement committed before, or together with, the
freeze of the pre-registration.
