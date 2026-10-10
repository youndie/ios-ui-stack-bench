---
id: B-02
title: "Choose the Swift bridge for B and C: Objective-C export with an adapter, SKIE, or Swift export"
status: done
priority: P0
size: XS
stage: stage-0-gate
---

# B-02 — Choose the Swift bridge for B and C

An open decision of the brief, and the one its own risk table flags: the A→B delta measures the
binding tool as much as Kotlin/Native, so the choice has to be made once, before the hello-world
variants of [B-05](B-05-hello-world-variants.md), and kept identical in B and C.

What the sources say about each option today is in
[research §1.8](../research/research-architecture.md). The recommendation there is the plain
Objective-C export with a thin hand-written Swift adapter that turns the shared module's
`StateFlow` into an `@Observable` model — because it is what the KMP wizard's native-UI template
generates (no SKIE, no Swift export), adds no compiler plugin whose support must track the Kotlin pin
(SKIE 0.10.15 claims 2.4.20, not the latest stable 2.4.21), and keeps B's SwiftUI views
byte-identical to A's. Swift export is Alpha by its own documentation.

- **The decision is the owner's**; this item records it and the reason, and B-01 pins the version.
- The rejected alternatives are written down with the reason they lost, so that a reader who
  prefers one can see what the A→B delta would have measured instead.
- Not covered: measuring more than one bridge. That would be a fourth variant, and the brief's
  non-goals exclude other stacks; if the owner wants it, it is an amendment and its own question.

- AC: the decision, its reason, and the rejected options with theirs, in this file and as a pin row
  in BRIEF.md.
- AC: the choice is one that compiles against the pinned Kotlin version — checked by building the
  hello-world B of B-05, not assumed from a compatibility table.
- Anchors: `shared/` (target), `apps/b-kmp-swiftui/` (target).

---

## Decision — 2026-10-10, the owner

**All three.** No option is rejected: each bridge becomes its own B arm over the same compiled
Kotlin module and the same SwiftUI views —
**B1** Objective-C export with a hand-written Swift adapter ([B-09](B-09-variant-b.md)),
**B2** SKIE ([B-20](B-20-variant-b2-skie.md)),
**B3** Swift export ([B-21](B-21-variant-b3-swift-export.md)).
C is built with the Objective-C export, so B1→C keeps the brief's "cost of Compose UI" isolated.

Recorded as amendment A1.1 in [BRIEF.md](../../BRIEF.md): RQ1's B − A and RQ5 are evaluated per
arm against the thresholds as written, with **no combined and no best-of verdict**; the session plan
for five apps under a cap of three, and the Kotlin pin SKIE allows, are B-01's
([research §2](../research/research-architecture.md), I5 and I14). The recommendation above is kept
as the reason B1 is the arm C is paired with.
