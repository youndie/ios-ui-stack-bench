#!/usr/bin/env python3
"""RQ0's recordings on a device, one arm at a time (B-06): every positive control, raw and exported.

    python3 harness/gate.py <out-dir> <device-udid> <arm> [<arm> ...]

For each arm: install it (and nothing else - a free account holds the runner and two arms, B-04), then
record, each into <out>/<arm>/<check>/<run>/:

    smooth-autoscroll/stall-50, stall-0
        Animation Hitches + Points of Interest, `xctrace record --launch`, the app scrolling its own
        list (`-benchAutoScroll 20`) with the stall injector at 50 ms and at 0 ms. Both instruments
        see the same stalls: the trace's hitches and the app's own frame log (A1.7).
    smooth-s2/stall-50, stall-0
        S2 through the harness with the same two stalls: the logger on the scenario RQ3 reads.
    startup/delay-200-<i>, delay-0-<i>, i = 1..5, interleaved
        App Launch + Points of Interest with `-benchDelayListMs 200` and without.
    memory/alloc-50-<i>, alloc-0-<i>, i = 1..3, interleaved
        Activity Monitor with `-benchAllocateMB 50` and without.
    size/
        the zip proxy of the device build, and of it with 1 MiB of seeded random bytes added.

Each recording keeps: the exported tables it is read through (`*.xml`, `xctrace export` verbatim),
`trace.sha256` of the bundle, `xctrace.log`,
and the app's own log of that launch (`app.ndjson`). `<out>/<arm>/header.json` is the run's header
(logs/README.md). Nothing is read or judged here - that is analysis/gate_reader.py's.

Recording, export, hashing and clean-up are harness/recording.py's: the bundles and xctrace's raw
kernel traces are deleted once exported (`KEEP_TRACES=1` keeps the bundles); the digest still ties
every export to its recording.

A recording that fails is kept as `attempt-<k>` with its log and retried once; a device has to be
unlocked, with UI automation allowed (B-04).
"""
import glob
import hashlib
import json
import os
import plistlib
import random
import shutil
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import recording  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLES = {"a-native": "a", "b1-objc": "b1", "b2-skie": "b2", "b3-swift-export": "b3", "c-kmp-cmp": "c"}


def sh(*cmd, check=True, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, check=check, **kw)




class Device:
    def __init__(self, udid):
        self.udid = udid
        self.seen = {}

    def wake(self):
        recording.wake(self.udid)

    def details(self):
        with tempfile.NamedTemporaryFile(suffix=".json") as f:
            sh("xcrun", "devicectl", "device", "info", "details", "--device", self.udid, "-j", f.name, "-q")
            r = json.load(open(f.name))["result"]
        return {"model": r["hardwareProperties"].get("marketingName"), "hw_machine": r["hardwareProperties"].get("productType"),
                "ios": r["deviceProperties"].get("osVersionNumber"), "ios_build": r["deviceProperties"].get("osBuildUpdate")}

    def installed(self):
        with tempfile.NamedTemporaryFile(suffix=".json") as f:
            sh("xcrun", "devicectl", "device", "info", "apps", "--device", self.udid, "-j", f.name, "-q")
            return [a["bundleIdentifier"] for a in json.load(open(f.name))["result"]["apps"]]

    def install(self, app):
        sh("xcrun", "devicectl", "device", "install", "app", "--device", self.udid, app)

    def uninstall(self, bundle):
        sh("xcrun", "devicectl", "device", "uninstall", "app", "--device", self.udid, bundle, check=False)

    def new_logs(self, bundle):
        """The app logs written since the last call, by file name (a device's clock is not the Mac's)."""
        tmp = tempfile.mkdtemp()
        sh("xcrun", "devicectl", "device", "copy", "from", "--device", self.udid, "--domain-type", "appDataContainer",
           "--domain-identifier", bundle, "--source", "Documents/bench", "--destination", tmp, check=False)
        paths = glob.glob(os.path.join(tmp, "**", "*.ndjson"), recursive=True)
        seen = self.seen.setdefault(bundle, set())
        fresh = sorted(p for p in paths if os.path.basename(p) not in seen)
        seen.update(os.path.basename(p) for p in paths)
        return fresh


def keep_app_log(device, bundle, where):
    logs = device.new_logs(bundle)
    if len(logs) == 1:
        shutil.copy(logs[0], os.path.join(where, "app.ndjson"))
    with open(os.path.join(where, "app-logs.txt"), "w") as f:
        f.write(f"{len(logs)} new app log(s): {[os.path.basename(p) for p in logs]}\n")


def record(device, arm, template, args, where, seconds):
    """One recording through harness/recording.py, then the app's own log of that launch."""
    bundle = f"io.github.youndie.iosbench.{BUNDLES[arm]}"
    arm_dir, check, run = where.split(os.sep)[-3:]
    ok = recording.record(device.udid, bundle, template, args, where, seconds, f"gate_{arm_dir}_{check}_{run}")
    for attempt in (1, 2):
        failed = os.path.join(where, f"attempt-{attempt}")
        if os.path.isdir(failed) and not os.path.exists(os.path.join(failed, "app-logs.txt")):
            keep_app_log(device, bundle, failed)
            break
    if ok:
        keep_app_log(device, bundle, where)
    return ok


def harness_s2(device, arm, stall, where):
    bundle = f"io.github.youndie.iosbench.{BUNDLES[arm]}"
    os.makedirs(where, exist_ok=True)
    device.wake()
    r = subprocess.run([os.path.join(ROOT, "harness", "run.sh"), arm, "S2", "-benchStallMs", str(stall)],
                       capture_output=True, text=True, env=dict(os.environ, DESTINATION=f"id={device.udid}"))
    open(os.path.join(where, "test.log"), "w").write(r.stdout + r.stderr)
    keep_app_log(device, bundle, where)


def zipped(app):
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "app.zip")
        subprocess.run(["zip", "-9", "-r", "-X", "-y", "-q", out, os.path.basename(app)], cwd=os.path.dirname(app), check=True)
        return os.path.getsize(out)


def size_control(app, where):
    """The size proxy's control (B-26's, here per arm): the zip of the device build before and after one
    extra file of 1 MiB of seeded random bytes. Only the difference is a gate number."""
    os.makedirs(where, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        copy = os.path.join(tmp, os.path.basename(app))
        shutil.copytree(app, copy, symlinks=True)
        before = zipped(copy)
        with open(os.path.join(copy, "control.bin"), "wb") as f:
            f.write(random.Random(20261010).randbytes(1 << 20))
        after = zipped(copy)
    json.dump({"added_bytes": 1 << 20, "zip_delta_bytes": after - before}, open(os.path.join(where, "size.json"), "w"), indent=1)


def gate_arm(device, arm, out, details, xcode, xctrace, commit):
    bundle = f"io.github.youndie.iosbench.{BUNDLES[arm]}"
    app = glob.glob(os.path.join(ROOT, "build", "DerivedData-device", arm, "Build", "Products", "Release-iphoneos", "*.app"))[0]
    info = plistlib.load(open(os.path.join(app, "Info.plist"), "rb"))
    exe = os.path.join(app, info["CFBundleExecutable"])
    arm_out = os.path.join(out, arm)
    os.makedirs(arm_out, exist_ok=True)
    others = [b for b in device.installed() if b.startswith("io.github.youndie.iosbench.") and b != bundle and not b.endswith(".xctrunner")]
    for b in others:
        device.uninstall(b)
    device.install(app)
    device.new_logs(bundle)  # what the app already holds is not this gate's
    json.dump({"device": details, "xcode": xcode, "xctrace": xctrace, "commit": commit, "bundle": bundle,
               "executable_sha256": hashlib.sha256(open(exe, "rb").read()).hexdigest(),
               "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
              open(os.path.join(arm_out, "header.json"), "w"), indent=1)

    for stall in (50, 0):
        print(f"{arm}: autoscroll, stall {stall} ms", flush=True)
        record(device, arm, "Animation Hitches", ["-benchAutoScroll", "20", "-benchStallMs", str(stall)],
               os.path.join(arm_out, "smooth-autoscroll", f"stall-{stall}"), 40)
    for stall in (50, 0):
        print(f"{arm}: S2, stall {stall} ms", flush=True)
        harness_s2(device, arm, stall, os.path.join(arm_out, "smooth-s2", f"stall-{stall}"))
    for i in range(1, 6):
        for delay in ((200, 0) if i % 2 else (0, 200)):
            print(f"{arm}: launch {i}, delay {delay} ms", flush=True)
            record(device, arm, "App Launch", ["-benchDelayListMs", str(delay)],
                   os.path.join(arm_out, "startup", f"delay-{delay}-{i}"), 12)
    for i in range(1, 4):
        for mib in ((50, 0) if i % 2 else (0, 50)):
            print(f"{arm}: memory {i}, allocate {mib} MiB", flush=True)
            record(device, arm, "Activity Monitor", ["-benchAllocateMB", str(mib)],
                   os.path.join(arm_out, "memory", f"alloc-{mib}-{i}"), 12)
    size_control(app, os.path.join(arm_out, "size"))
    head = json.load(open(os.path.join(arm_out, "header.json")))
    head["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    json.dump(head, open(os.path.join(arm_out, "header.json"), "w"), indent=1)


def main():
    out, udid, arms = os.path.abspath(sys.argv[1]), sys.argv[2], sys.argv[3:]
    if not arms or any(a not in BUNDLES for a in arms):
        raise SystemExit(f"usage: gate.py <out> <udid> <arm>...; arms: {', '.join(BUNDLES)}")
    if sh("git", "-C", ROOT, "status", "--porcelain", "--", "apps", "shared", "bridge-objc", "bridge-skie",
          "bridge-swift-export", "compose-ui", "harness").stdout.strip():
        raise SystemExit("the apps' or the harness's sources are not committed: a header names the commit they were built from")
    device = Device(udid)
    details = device.details()
    xcode = " ".join(sh("xcodebuild", "-version").stdout.split())
    xctrace = sh("xcrun", "xctrace", "version").stdout.strip()
    commit = sh("git", "-C", ROOT, "rev-parse", "HEAD").stdout.strip()
    for arm in arms:
        gate_arm(device, arm, out, details, xcode, xctrace, commit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
