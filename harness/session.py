#!/usr/bin/env python3
"""Run one measurement session from a plan: install, rotated runs, collection, runs.csv (B-25).

    python3 harness/session.py <plan.json>

A plan names the device, the arms, the runs per scenario and where the output goes:

    {
      "session": "older-1",
      "device": "older",                       older | newer | simulator
      "destination": "platform=iOS Simulator,id=<udid>"   or "id=<device udid>"
      "udid": "<udid>",
      "apps": "build/DerivedData",             <apps>/<arm>/Build/Products/<config>/<Product>.app
      "arms": ["a-native", "b1-objc", "c-kmp-cmp"],
      "runs": {"S1": 20, "S2": 10, "S3": 10, "S4": 10},
      "out": "logs/b-17/2026-10-20-older-1"    refused under logs/ for a simulator
    }

What it does, in the brief's protocol:
- installs every arm of the plan at the start, never in the middle, and records the sha256 of each
  installed main executable;
- runs each scenario's batches with the arms in rotated order - run r starts at arm r mod n, so A->B->C,
  B->C->A, C->A->B - and marks each arm's first run of a scenario as the warm-up (`counted=0`);
- after each run, pulls the one log that run produced, reads it (analysis/inapp_reader.py) and decides
  (`decide` below): count it, repeat it, or stop the session;
- appends one row per attempt to <out>/runs.csv, the input of analysis/verdicts.py, and keeps every
  log and its CSVs under <out>/<scenario>/<arm>/run-<n>-attempt-<k>/.

A device is driven through `xcrun devicectl`; that half runs for the first time in B-04/B-06 and is
the one part of this file not yet exercised.
"""
import csv
import glob
import hashlib
import json
import os
import plistlib
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
import inapp_reader  # noqa: E402

BUNDLES = {"a-native": "a", "b1-objc": "b1", "b2-skie": "b2", "b3-swift-export": "b3", "c-kmp-cmp": "c"}
SCENARIOS = ("S1", "S2", "S3", "S4")
MAX_ATTEMPTS = 3


def decide(summary, kind):
    """What to do with one attempt, from the app's own log (brief: Devices; Runs and statistics).

    stop     the session cannot go on as specified: Low Power Mode on, or a battery under 50 %
             on a device (a simulator reports -1, unknown)
    repeat   the run does not count and is run again: the reader marked it invalid, or the thermal
             state was not nominal at any point of it
    count    otherwise
    """
    if summary.get("low_power") == 1:
        return "stop", "Low Power Mode is on"
    battery = summary.get("battery")
    if kind == "device" and (battery == "" or battery is None or (battery != -1 and battery < 0.5)):
        return "stop", f"battery {battery}"
    if summary.get("valid") != 1:
        return "repeat", f"invalid: {summary.get('reason')}"
    if summary.get("thermal_worst") != "nominal":
        return "repeat", f"thermal state reached {summary.get('thermal_worst')}"
    return "count", ""


def rotation(arms, run):
    k = run % len(arms)
    return arms[k:] + arms[:k]


def sh(*cmd, env=None, check=True):
    return subprocess.run(cmd, capture_output=True, text=True, check=check, env=env)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class Target:
    def __init__(self, plan):
        self.udid = plan["udid"]
        self.kind = "simulator" if plan["device"] == "simulator" else "device"
        self.config = "Release-iphonesimulator" if self.kind == "simulator" else "Release-iphoneos"
        self.apps = os.path.join(ROOT, plan.get("apps", "build/DerivedData"))
        # Logs already pulled, per bundle: a run's log is the one file that is new since the last
        # pull - by name, not by the timestamp in it, because a device's clock is not the Mac's.
        self.seen = {}

    def app(self, arm):
        found = glob.glob(os.path.join(self.apps, arm, "Build", "Products", self.config, "*.app"))
        if len(found) != 1:
            raise SystemExit(f"{arm}: expected one built .app under {self.apps}/{arm}, found {len(found)}")
        return found[0]

    def install(self, arm):
        app = self.app(arm)
        info = plistlib.load(open(os.path.join(app, "Info.plist"), "rb"))
        digest = sha256(os.path.join(app, info["CFBundleExecutable"]))
        if self.kind == "simulator":
            sh("xcrun", "simctl", "install", self.udid, app)
        else:
            sh("xcrun", "devicectl", "device", "install", "app", "--device", self.udid, app)
        return digest

    def pull_logs(self, bundle, into):
        """Copy the arm's bench/ directory into `into`; return the .ndjson paths."""
        os.makedirs(into, exist_ok=True)
        if self.kind == "simulator":
            data = sh("xcrun", "simctl", "get_app_container", self.udid, bundle, "data").stdout.strip()
            for f in glob.glob(os.path.join(data, "Documents", "bench", "*.ndjson")):
                with open(f, "rb") as src, open(os.path.join(into, os.path.basename(f)), "wb") as dst:
                    dst.write(src.read())
        else:
            sh("xcrun", "devicectl", "device", "copy", "from", "--device", self.udid,
               "--domain-type", "appDataContainer", "--domain-identifier", bundle,
               "--source", "Documents/bench", "--destination", into)
        return glob.glob(os.path.join(into, "**", "*.ndjson"), recursive=True)

    def new_logs(self, bundle, into):
        paths = self.pull_logs(bundle, into)
        seen = self.seen.setdefault(bundle, set())
        fresh = [p for p in paths if os.path.basename(p) not in seen]
        seen.update(os.path.basename(p) for p in paths)
        return fresh


def run_scenario(plan, arm, scenario):
    env = dict(os.environ, DESTINATION=plan["destination"])
    out = sh(os.path.join(ROOT, "harness", "run.sh"), arm, scenario, env=env, check=False).stdout
    return "passed" if "passed (" in out else ("failed" if "failed (" in out else "no result")


def main():
    plan = json.load(open(sys.argv[1]))
    target = Target(plan)
    out = os.path.join(ROOT, plan["out"])
    if target.kind == "simulator" and os.path.abspath(out).startswith(os.path.join(ROOT, "logs") + os.sep):
        raise SystemExit("refusing to write simulator output under logs/")
    os.makedirs(out, exist_ok=True)
    arms = plan["arms"]
    digests = {arm: target.install(arm) for arm in arms}
    for arm in arms:  # whatever logs the installed apps already hold are not this session's
        with tempfile.TemporaryDirectory() as tmp:
            target.new_logs(f"io.github.youndie.iosbench.{BUNDLES[arm]}", tmp)
    with open(os.path.join(out, "session.json"), "w") as f:
        json.dump({"plan": plan, "installed": digests, "started": time.time()}, f, indent=1)
    print(f"session {plan['session']}: installed {', '.join(f'{a} {d[:12]}' for a, d in digests.items())}")

    rows = []
    for scenario in SCENARIOS:
        for run in range(plan["runs"].get(scenario, 0)):
            for arm in rotation(arms, run):
                for attempt in range(1, MAX_ATTEMPTS + 1):
                    result = run_scenario(plan, arm, scenario)
                    bundle = f"io.github.youndie.iosbench.{BUNDLES[arm]}"
                    with tempfile.TemporaryDirectory() as tmp:
                        logs = target.new_logs(bundle, tmp)
                        where = os.path.join(out, scenario, arm, f"run-{run}-attempt-{attempt}")
                        os.makedirs(where, exist_ok=True)
                        if len(logs) != 1:
                            summary = {"valid": 0, "reason": f"{len(logs)} logs from one run"}
                        else:
                            with open(logs[0], "rb") as src, open(os.path.join(where, "app.ndjson"), "wb") as dst:
                                dst.write(src.read())
                            lines = inapp_reader.load(os.path.join(where, "app.ndjson"))
                            summary = inapp_reader.summarise(lines, scenario)
                    action, why = decide(summary, target.kind)
                    if result != "passed" and action == "count":
                        action, why = "repeat", f"UI test {result}"
                    row = {"device": plan["device"], "session": plan["session"], "arm": arm, "scenario": scenario,
                           "run": run, "attempt": attempt, "counted": int(run > 0 and action == "count"),
                           "decision": action, "why": why, "test": result,
                           "installed_sha256": digests[arm], **summary}
                    row["valid"] = int(summary.get("valid") == 1 and action == "count")
                    rows.append(row)
                    print(f"{scenario} run {run} {arm} attempt {attempt}: {action} {why}".rstrip())
                    if action == "stop":
                        write(out, rows)
                        raise SystemExit(f"session stopped: {why}")
                    if action == "count":
                        break
    write(out, rows)
    print(f"session {plan['session']}: {len(rows)} attempts, runs.csv in {out}")
    return 0


def write(out, rows):
    fields = []
    for r in rows:
        fields += [k for k in r if k not in fields]
    with open(os.path.join(out, "runs.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    sys.exit(main())
