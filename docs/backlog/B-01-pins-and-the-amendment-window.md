---
id: B-01
title: "Pin the stand, settle the brief's incoherences as amendments, and close the window"
status: open
priority: P0
size: S
stage: stage-0-gate
blocked_by: [B-04]
---

# B-01 — Pin the stand, settle the brief's incoherences, close the amendment window

The brief fixes its thresholds "before any code exists", and that is only worth something while
nothing it governs can still move. Before the first number three things are therefore missing: the
pins the brief left as "latest stable" and "which iPhones", the owner's answers to its four open
decisions, and an answer to each incoherence in
[research §2](../research/research-architecture.md) — places where the frozen text cannot be
applied as written (a kill criterion counted in runs that the plan never makes, a statistics rule
that does not fit an absolute threshold, a device not named for three of five questions).

- **The decision and its reason.** Every incoherence is settled as an amendment in
  [BRIEF.md](../../BRIEF.md), dated, with the evidence that forced it — never by editing
  `docs/research/source-brief.md`, which `make check` holds byte for byte. An amendment that can
  only push a verdict towards green publishes the verdict under the original rule beside it.
- The rejected alternative is settling them when the numbers arrive: each one is a choice that a
  number would make for us, which is exactly what the window exists to forbid.
- Not covered: changing a threshold. None of §2's items asks for one, and an item that wants to
  move a bar goes to the owner as a `question`, not into this one.

- AC: BRIEF.md carries the record line `brief_freeze.py --record` printed, committed together with
  the frozen file and before anything under `logs/` other than its README.
- AC: every pin row has a value and where it came from — Xcode (a released build, not a beta; see
  research §1.2), Kotlin, Compose Multiplatform, SKIE and the Swift export mode of the three bridge
  arms ([B-02](B-02-swift-bridge.md), amendment A1.1), both devices with model, `hw.machine` and iOS
  build — each a version plus the commit or build number behind it, because a tag moves.
- AC: the Kotlin pin is the newest version every bridge arm compiles against, shown by building the
  hello-world arms of [B-05](B-05-hello-world-variants.md) — not read off a compatibility page
  (research §2, I14). If it is not the latest stable, the deviation is an amendment with its reason.
- AC: the session plan for five apps under the install cap — which arms share a session, A in every
  one, B1 with C — written as an amendment once [B-04](B-04-free-provisioning-probe.md) has measured
  the cap (research §2, I5).
- AC: every item of research §2 is either an amendment in BRIEF.md or recorded there as "left as
  written", with the reason.
- AC: the first commit that adds a measurement under `logs/` is named in BRIEF.md as the window's
  close, and `make check` (`brief_freeze.py --history --window logs`) is green on it.
- Anchors: `BRIEF.md`, `docs/research/source-brief.md`, `scripts/brief_freeze.py`.

---

## Progress — 2026-10-11

The owner approved every proposal of research §2 (I1–I15) and D3, D4: amendment A1.4 in BRIEF.md.
The pins are filled by version and commit, Kotlin at 2.4.20. **Still open in this item:**
- I5's session plan, which needs B-04's measured cap;
- I12's tolerance number, which B-11 sets;
- both device rows;
- the window's close at the first file under `logs/`.

All of it waits for the devices. The status stays `open`.
