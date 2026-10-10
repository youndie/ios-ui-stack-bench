---
id: B-04
title: "What free provisioning allows on the devices: apps per device, the test runner, Instruments on Release"
status: open
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
