#!/usr/bin/env python3
"""Summarise an arm's latest instrumentation log on the booted simulator, in counts only.

A development check that a scenario left the markers its reader needs (B-13); it prints counts and
phases, never timings, because simulator numbers are not reported.

    python3 scripts/log-summary.py io.github.youndie.iosbench.a
"""
import glob
import json
import os
import subprocess
import sys

bundle = sys.argv[1]
data = subprocess.run(["xcrun", "simctl", "get_app_container", "booted", bundle, "data"],
                      capture_output=True, text=True, check=True).stdout.strip()
path = max(glob.glob(os.path.join(data, "Documents", "bench", "*.ndjson")), key=os.path.getmtime)
lines = [json.loads(line) for line in open(path)]
kinds = {}
for line in lines:
    kinds[line["k"]] = kinds.get(line["k"], 0) + 1
phases = {}
for line in lines:
    if line["k"] == "mark":
        phases[line["name"]] = phases.get(line["name"], 0) + 1
scrolls = [line for line in lines if line["k"] == "scroll"]
print(f"{bundle}: {os.path.basename(path)}")
print(f"  lines {kinds}")
print(f"  markers {phases}")
if scrolls:
    begins = sum(1 for s in scrolls if s["phase"] == "begin")
    ends = [s for s in scrolls if s["phase"] == "end"]
    fields = sorted(k for k in ends[-1] if k not in ('k', 't')) if ends else []
    print(f"  scroll begin {begins}, end {len(ends)}; fields of an end: {fields}")
