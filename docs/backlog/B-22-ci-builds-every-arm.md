---
id: B-22
title: "CI builds every arm on macOS, so a green pull request means the apps still build"
status: done
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

---

## Findings — 2026-10-10

**Done.** `.github/workflows/apps.yaml`, job `build`, on GitHub's `xcode-27` image (a preview label,
actions/runner-images#14404): it selects the Xcode whose build is the pinned `27A266a` — the image
carries it as `/Applications/Xcode_27.0.0.app` — runs the shared module's tests on the simulator and
`scripts/build-arms.sh`, and uploads the per-arm build logs when it fails.

- AC (red when an arm breaks): a throwaway branch `tmp/b-22-red-control` added a type error to B2's
  `BenchApp.swift`; run 38071924512 failed at "Build every arm" with `b2-skie: FAILED` and the
  compiler's error, while the other four arms built. The branch is deleted.
- AC (the log names the toolchain and each arm): the first green run, 38070613051, prints the Xcode
  build, the simulator SDK, Gradle's `:shared:iosSimulatorArm64Test` and one line per arm.
- AC (required by the merge rule): [CLAUDE.md](../../CLAUDE.md) now names both checks, `check` and
  `build`, as what "green on the head commit" means.

The Kotlin/Native toolchain is cached on the version catalog's hash, so a Kotlin bump downloads it
once. The image is a preview; if GitHub drops the label or the pinned Xcode from it, the job turns red
at its first step with `no Xcode with build 27A266a`, which is the intended behaviour.
