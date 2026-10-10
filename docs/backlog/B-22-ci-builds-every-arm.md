---
id: B-22
title: "CI builds every arm on macOS, so a green pull request means the apps still build"
status: open
priority: infra
size: S
stage: stage-1-build
blocked_by: [B-05]
---

# B-22 — CI builds every arm

The loop merges its own pull requests on a green head commit (owner, 2026-10-10), and until this
item the only CI job is the documentation gate on Ubuntu: a pull request that breaks the Kotlin
module or an Xcode project would come back green. "Green" has to include the build of every arm.

- **The decision and its reason.** One job on a GitHub-hosted macOS runner (free for a public
  repository) runs the same build script a contributor runs — Release configuration, simulator SDK,
  no signing — for A, B1, B2, B3 and C, plus the Kotlin module's tests and the readers' controls once
  they exist. The script is the gate, the workflow only calls it, as `make check` is for the documents.
- **The Xcode build is checked, not assumed.** The script compares `xcodebuild -version` with the
  pin in BRIEF.md (`27A266a`) and fails on any other build. A runner image without that Xcode makes
  the job red with a message saying so — which is the honest state — rather than green on another
  toolchain. If no hosted image carries it, the job is marked as such in this file and the PR body
  carries the local run's log instead, until one does.
- Not covered: devices, signing, measurements. CI never produces a number.

- AC: a pull request that breaks any arm's build is red in CI (shown once on a throwaway branch).
- AC: the job's log names the Xcode build, the Kotlin version and each arm's result.
- AC: the job is required by the merge rule of [CLAUDE.md](../../CLAUDE.md) — "green on the head
  commit" means both jobs.
- Anchors: `.github/workflows/`, `scripts/` (build script, target).
