# docs — ios-ui-stack-bench

A measurement study, not a product, so most of the usual layers are absent: there are no features,
screens or endpoints a user reaches. The apps, the harness and the readers are code. Each script's
header says what it does, and [../CLAUDE.md](../CLAUDE.md) ("Where the work runs") maps them. This
folder holds the research, the backlog and the flags.

| Document | What it is |
|---|---|
| [research/source-brief.md](research/source-brief.md) | The brief as received, frozen byte for byte. |
| [../BRIEF.md](../BRIEF.md) | The freeze record, the pins, the answers to what the brief believed, the amendments. |
| [research/research-architecture.md](research/research-architecture.md) | The evidence the study starts from, the brief's incoherences, decisions and risks. **Start here.** |
| [../backlog.md](../backlog.md) | The work queue: goal, stages, kill-criterion owners, decisions, the generated index. |
| [backlog/](backlog/) | One file per item. |
| [../README.md](../README.md) | The verdicts so far, generated from `logs/` by `analysis/readme_results.py`. |
| [../GATE.md](../GATE.md) | RQ0: every control on the iPhone XS, generated from `logs/b-06/`. |
| [flags.md](flags.md) | Every place an arm departs from its stack's default, and why. |
| [../logs/](../logs/) | Raw runs, one directory per item — the deliverable. |

Conventions: `id` in the frontmatter equals the filename; links between documents are ordinary
markdown links; every document carries paths into the code or addresses into the artefacts it was
checked against. Language: English. Templates are in [templates/](templates/), including the
results template the write-up starts from.

## Checks

```bash
pip install pyyaml
make check      # the gate, then the reports: what CI runs
make fix        # regenerate the backlog index
```

## Coverage map

### Research (2)

- [x] [research-architecture](research/research-architecture.md) — prior work as its sources report it, the stand, Apple's launch and hitch definitions, free provisioning, 120 Hz and Liquid Glass, the Swift bridge, linkage and size, Kotlin/Native memory; the brief's incoherences I1–I15; decisions D1–D8; risks, each with its outcome
- [x] [source-brief](research/source-brief.md) — the pre-registration as received on 2026-10-10, frozen and hashed by `make check`
