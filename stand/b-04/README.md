# B-04 — what free provisioning allows on the devices

Probes of the stand, not measurements of the arms: they live here, outside `logs/`, so they do not
close the amendment window (logs/README.md). Every file is the verbatim output of the command it
names, captured on the Mac that drove the device.

| File | What it shows |
|---|---|
| `2026-10-11-xs-install-cap.log` | A, B1, B2 install on the XS; B3 and C are refused with the free-profile limit, listing the three app identifiers that hold the slots |
| `2026-10-11-xs-runner.log` | the UI-test runner is refused by the same limit with three arms installed, and installs by hand once a slot is free; `xcodebuild` itself cannot install it ("Root install style is not supported") |
| `2026-10-11-pro-runner.log` | the same `xcodebuild` failure on the iPhone 17 Pro (iOS 26.6.2) |
| `2026-10-11-xs-xctrace.log` | App Launch, Animation Hitches and Allocations recordings of arm A on the XS, launched by `xctrace` itself; two first attempts time out while the device has no tunnel |
| `2026-10-11-xs-runner-xcode26.log` | the runner built and run with Xcode 26.6 fails the same way: the cause is not Xcode 27.0 |
| `2026-10-11-xs-runner-dstroot.log` | the cause, `DSTROOTPath` in the `.xctestrun`, and S1–S4 of arm A passing on the XS without it, with the reader's validity check of the four app logs |
| `2026-10-11-pro-runner-dstroot.log` | S1 and S2 of arm A passing on the iPhone 17 Pro through the same fix; the app's frame logger at 120 Hz there |
