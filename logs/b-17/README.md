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

**The sessions.** `xs-1` is {A, C} with the runner, 2026-10-12. `xs-2` is {A, B1, B2} without it,
2026-10-12: it was stopped two S4p runs short, and its `runs.csv` was rebuilt by
`harness/session.py --rebuild`. `xs-3` is {A, B3, C} without it, 2026-10-13. Each has
`verdicts.txt` and `verdicts.csv` from `analysis/verdicts.py`. By A2.5, RQ2–RQ4 are decided by
`xs-1`, `xs-3` repeats them, and RQ5 reads each B arm's own session.
