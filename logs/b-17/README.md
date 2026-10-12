# B-17 — the sessions on the iPhone XS

`plans/` holds the session plans: the pilot (`pilot-1` … `pilot-3`) and the five pair sessions of
A1.5 (`xs-1` … `xs-5`). Each session's directory holds `session.json` (the plan, the installed
executables' digests, the device, Xcode, `xctrace`, the commit), `runs.csv`, and one directory per
attempt: the app's log, and for S1, S2p and S4p the exported trace tables with the trace's digest.

**The pilot (2026-10-12)**, asked for by the owner before the full sessions: every arm, S1, S2p and
S4p, two runs each, so one counted run after the warm-up. Three short sessions, because a free account
holds two arms: {A, C}, {B1, B2}, {B3}. `pilot.md` is `analysis/pilot_table.py`'s table of them. It is
an orientation and not a verdict. One run cannot carry a median or an interval, and
`analysis/verdicts.py` reads none of it. The B arms were not in A's session. The verdicts come from
the five pair sessions alone.
