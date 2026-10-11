---
id: B-04
title: "What free provisioning allows on the devices: apps per device, the test runner, Instruments on Release"
status: wip
priority: P0
size: S
stage: stage-0-gate
---

# B-04 — What free provisioning allows on the devices

The brief's whole method rests on a free Apple ID, and three of its premises about that are believed
rather than checked ([research §1.5](../research/research-architecture.md)): how many apps a
Personal Team may have installed on one device at once, whether the UI-test runner counts as one of
them, and whether Instruments can record a **Release** build signed by a Personal Team. The first
two decide whether the protocol is possible at all as written: the brief rotates A→B→C inside a
session and forbids reinstalling mid-session, which needs all three variants installed together —
and the UI-test runner beside them.

- **The decision and its reason.** Probe it with empty apps on both devices, before a line of the
  study's code exists. If the cap bites, the protocol has to change, and that is an amendment made
  inside the window — not a discovery in P3 that turns into reinstalling between runs.
- Fixed bundle ids are chosen here and never changed: a free account also limits how many App IDs it
  may create per week, and a variant renamed mid-study spends them.
- Not covered: the study's instruments. Whether each metric can be captured is RQ0, [B-06](B-06-rq0-the-gate.md).

- The probe's output goes to `stand/b-04/`, not `logs/`: it measures the stand, not an arm, and a
  file under `logs/` would close the amendment window before B-01 can use this item's answer.
- AC: on each device, the number of Personal-Team apps that install and launch together, found by
  installing empty apps until the device or Xcode refuses, with the refusal's exact text in the log.
- AC: the same with an XCUITest target installed — does its runner count against the cap, and can
  one UI-test target drive three apps by bundle id (`XCUIApplication(bundleIdentifier:)`).
- AC: an empty Release-configuration app, signed by the Personal Team, recorded on the device with
  `xctrace record --template 'App Launch'`, `'Animation Hitches'` and `'Allocations'`; for each, it
  records or fails, and the failure is logged verbatim. The `get-task-allow` entitlement of the
  installed build is printed (`codesign -d --entitlements`), because it is what some instruments need.
- AC: the profile's expiry date as installed, and the App ID count the account has left.
- AC: the cap is three by Apple's page, and the study has five apps since amendment A1.1, so a
  session plan is needed whatever the runner does; this item hands B-01 the measured number of free
  slots beside the runner, and the options it allows, with what each costs the interleaving.
- Anchors: `stand/b-04/` (target), `harness/` (target).

---

## Iteration 1 — 2026-10-11

Devices: an iPhone XS (`iPhone11,2`, iOS 18.7.3, 22H217) and an iPhone 17 Pro (`iPhone18,1`, iOS 26.6.2,
23G90, 120 Hz). Both are in Developer Mode, and the Personal Team is `P3Y5X9576J` (git-ignored
`Local.xcconfig`). The raw output is in [stand/b-04/](../../stand/b-04/README.md).

**Answered:**
- **The cap is three apps per device**, enforced at install. On the XS, A, B1 and B2 installed; B3 and
  C were refused with "This device has reached the maximum number of installed apps using a free
  developer profile". The refusal lists the three identifiers holding the slots, and comes from
  `MIFreeProfileValidatedAppTracker`.
- **The UI-test runner takes a slot.** With three arms installed, `devicectl` refused to install it
  with the same message. Once one arm was removed, it installed. So a session holds **the runner and
  two arms** (A1.4 I5's plan follows from this).
- **A Release build signed by a Personal Team carries `get-task-allow = true`.** That is the
  entitlement Instruments needs to attach. It was read with `codesign` from the device build of A.
- **`devicectl` install, launch and log pull work on the device.** The pull gives the app's own
  header: `iPhone11,2`, iOS 18.7.3, 60 fps, nominal, battery 1.0.
- **An App Launch recording works on the XS**, launched by `xctrace` itself with no runner. It holds
  `life-cycle-period` and `time-profile`.
- The App ID budget: six used (a, b1, b2, b3, c, harness.xctrunner), with probes run on the real
  bundle ids rather than empty apps so as not to spend more.

**Blocking: `xcodebuild` cannot run the UI tests on either device.** Every way tried fails before the
first test with "Root install style is not supported on this device. To install internal content, the
device must allow installing app bundles and roots, and be running an internal OS build":
- the host-less harness, both through the scheme and through the `.xctestrun`;
- with the runner already installed by hand;
- with a patched `.xctestrun`;
- with A declared as the UI target app;
- on the iPhone 17 Pro as well as the XS;
- with a throwaway project in which the UI tests are hosted by arm A (not committed).

The runner itself installs and is signed and provisioned. No public report of the message was found.
Without the runner there is no S2–S4 on a device, so this item stays `wip`, and the question goes to
the owner.
