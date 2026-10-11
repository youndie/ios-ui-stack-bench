#!/usr/bin/env python3
"""B-16's recordings on the device: the ruler, the runner's contamination, the study's own instruments.

    python3 harness/dryrun.py <out-dir> <device-udid> [ruler] [runner] [instruments]

Arm A only, so every difference measured here is the stand's, never a stack's. Into <out>:

    ruler/          a whole session of A alone (harness/session.py, the brief's run counts, no
                    cross-checks). analysis/dryrun_reader.py splits its counted runs into two
                    interleaved halves and reads A against A.
    runner/with-<i>, without-<i>, i = 1..5, interleaved
                    an idle launch, the list shown and then 30 s untouched: once launched by the UI-test
                    runner (`harness/run.sh a-native IDLE`), once by `devicectl` with no runner. The app's
                    own CPU time and footprint in each are kill criterion 5's figures (I6).
    instruments/launch-on-<i>, launch-off-<i>, i = 1..5
                    App Launch with Points of Interest, the app's frame logger and footprint sampler on and
                    off (`-benchInstrumentsOff 1`);
    instruments/hitches-on-<i>, hitches-off-<i>, i = 1..3
                    Animation Hitches on the self-scrolling run, on and off.

Each recording keeps what harness/recording.py keeps, plus the app's log of that launch.
"""
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import recording  # noqa: E402

BUNDLE = "io.github.youndie.iosbench.a"
APP = "build/DerivedData-device/a-native/Build/Products/Release-iphoneos"


def sh(*cmd, check=True, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, check=check, **kw)


class Logs:
    def __init__(self, udid):
        self.udid, self.seen = udid, set()

    def new(self):
        tmp = tempfile.mkdtemp()
        sh("xcrun", "devicectl", "device", "copy", "from", "--device", self.udid, "--domain-type", "appDataContainer",
           "--domain-identifier", BUNDLE, "--source", "Documents/bench", "--destination", tmp, check=False)
        paths = glob.glob(os.path.join(tmp, "**", "*.ndjson"), recursive=True)
        fresh = sorted(p for p in paths if os.path.basename(p) not in self.seen)
        self.seen.update(os.path.basename(p) for p in paths)
        return fresh

    def keep(self, where):
        fresh = self.new()
        if len(fresh) == 1:
            shutil.copy(fresh[0], os.path.join(where, "app.ndjson"))
        open(os.path.join(where, "app-logs.txt"), "w").write(f"{len(fresh)} new app log(s)\n")


def ruler(out, udid):
    plan = {"session": "ruler", "device": "older", "destination": f"id={udid}", "udid": udid, "apps": "build/DerivedData-device",
            "arms": ["a-native"], "runs": {"S1": 20, "S2": 10, "S3": 10, "S4": 10}, "crosscheck": False,
            "out": os.path.join(out, "ruler")}
    path = os.path.join(out, "ruler-plan.json")
    json.dump(plan, open(path, "w"), indent=1)
    subprocess.run([sys.executable, os.path.join(ROOT, "harness", "session.py"), path], check=True)


def idle_without_runner(udid, where):
    with tempfile.NamedTemporaryFile(suffix=".json") as f:
        sh("xcrun", "devicectl", "device", "process", "launch", "--device", udid, "--terminate-existing", "-j", f.name,
           "--", BUNDLE, "-benchScenario", "idle")  # without `--` devicectl reads the app's arguments as its own
        pid = json.load(open(f.name))["result"]["process"]["processIdentifier"]
    time.sleep(32)  # the runner's run: the list (about 1 s), then 30 s untouched
    sh("xcrun", "devicectl", "device", "process", "terminate", "--device", udid, "--pid", str(pid), check=False)
    open(os.path.join(where, "launch.txt"), "w").write(f"devicectl launch, pid {pid}, terminated after 32 s\n")


def runner(out, udid, logs):
    for i in range(1, 6):
        for mode in (("with", "without") if i % 2 else ("without", "with")):
            where = os.path.join(out, "runner", f"{mode}-{i}")
            os.makedirs(where, exist_ok=True)
            print(f"runner {i}: {mode}", flush=True)
            recording.wake(udid)
            if mode == "with":
                r = subprocess.run([os.path.join(ROOT, "harness", "run.sh"), "a-native", "IDLE"], capture_output=True, text=True,
                                   env=dict(os.environ, DESTINATION=f"id={udid}"))
                open(os.path.join(where, "test.log"), "w").write(r.stdout + r.stderr)
            else:
                idle_without_runner(udid, where)
            time.sleep(5)
            logs.keep(where)


def instruments(out, udid, logs):
    for kind, template, args, count, seconds in (("launch", "App Launch", [], 5, 10),
                                                 ("hitches", "Animation Hitches", ["-benchAutoScroll", "20"], 3, 40)):
        for i in range(1, count + 1):
            for state in (("on", "off") if i % 2 else ("off", "on")):
                where = os.path.join(out, "instruments", f"{kind}-{state}-{i}")
                print(f"instruments {kind} {i}: {state}", flush=True)
                extra = ["-benchInstrumentsOff", "1"] if state == "off" else []
                recording.record(udid, BUNDLE, template, args + extra, where, seconds, f"dryrun_{kind}_{state}_{i}")
                logs.keep(where)


def main():
    out, udid = os.path.abspath(sys.argv[1]), sys.argv[2]
    parts = sys.argv[3:] or ["ruler", "runner", "instruments"]
    if sh("git", "-C", ROOT, "status", "--porcelain", "--", "apps", "harness", "analysis").stdout.strip():
        raise SystemExit("commit the apps, the harness and the readers first: the logs name the commit they came from")
    os.makedirs(out, exist_ok=True)
    app = glob.glob(os.path.join(ROOT, APP, "*.app"))[0]
    for other in ("b1", "b2", "b3", "c"):
        sh("xcrun", "devicectl", "device", "uninstall", "app", "--device", udid, f"io.github.youndie.iosbench.{other}", check=False)
    sh("xcrun", "devicectl", "device", "install", "app", "--device", udid, app)
    head = {"commit": sh("git", "-C", ROOT, "rev-parse", "HEAD").stdout.strip(),
            "xcode": " ".join(sh("xcodebuild", "-version").stdout.split()), "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    json.dump(head, open(os.path.join(out, "header.json"), "w"), indent=1)
    logs = Logs(udid)
    logs.new()
    if "ruler" in parts:
        ruler(out, udid)
        logs.new()  # the session's logs are its own
    if "runner" in parts:
        runner(out, udid, logs)
    if "instruments" in parts:
        instruments(out, udid, logs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
