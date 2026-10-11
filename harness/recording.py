#!/usr/bin/env python3
"""One `xctrace` recording on a device, exported and cleaned up (B-06, B-24). Used by harness/gate.py
and harness/session.py.

`record()` launches the app itself (`xctrace record --launch`) - no recording survives beside the
UI-test runner on a device (A1.7) - adds Points of Interest to every template that has no signposts
of its own, exports the tables the readers need (`<schema>.xml`, verbatim), writes the bundle's
`sha256`, and then deletes the bundle and the raw kernel traces `xctrace` leaves in `$TMPDIR`
(`instruments*.ktrace`, 1-2.5 GB each, which filled the Mac's disk during B-06). A failed recording
is kept as `attempt-<k>/xctrace.log` and retried once. `KEEP_TRACES=1` keeps the bundles.
"""
import glob
import hashlib
import os
import shutil
import subprocess
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRACES = os.path.join(ROOT, "build", "traces")
TABLES = {
    "Animation Hitches": ["hitches-summary", "PointsOfInterestEvents"],
    "App Launch": ["life-cycle-period", "PointsOfInterestEvents"],
    "Activity Monitor": ["activity-monitor-process-live"],
}
NO_SIGNPOSTS = {"Animation Hitches", "App Launch"}


def tree_sha256(path):
    """One digest for a bundle: sha256 over 'relative path, file sha256' lines in path order."""
    lines = []
    for base, _, files in sorted(os.walk(path)):
        for name in sorted(files):
            full = os.path.join(base, name)
            with open(full, "rb") as f:
                lines.append(f"{os.path.relpath(full, path)} {hashlib.sha256(f.read()).hexdigest()}")
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()


def wake(udid):
    # xctrace lists a paired device as offline until its tunnel is open (B-04).
    subprocess.run(["xcrun", "devicectl", "device", "info", "apps", "--device", udid], capture_output=True)


def clean_tmp(older_than_s=0):
    """Delete the raw kernel traces xctrace leaves behind in $TMPDIR."""
    now = time.time()
    for path in glob.glob(os.path.join(tempfile.gettempdir(), "instruments*.ktrace")):
        try:
            if now - os.path.getmtime(path) >= older_than_s:
                shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)
        except OSError:
            pass


def record(udid, bundle, template, args, where, seconds, name):
    """Record `bundle` launched with `args` into `where`; True when a recording was exported."""
    os.makedirs(where, exist_ok=True)
    os.makedirs(TRACES, exist_ok=True)
    for attempt in (1, 2):
        trace = os.path.join(TRACES, f"{name}-{attempt}.trace")
        shutil.rmtree(trace, ignore_errors=True)
        wake(udid)
        cmd = ["xcrun", "xctrace", "record", "--template", template, "--device", udid, "--time-limit", f"{seconds}s", "--output", trace]
        if template in NO_SIGNPOSTS:
            cmd += ["--instrument", "Points of Interest"]
        cmd += ["--launch", "--", bundle, *args]
        r = subprocess.run(cmd, capture_output=True, text=True)
        log = f"$ {' '.join(cmd[1:])}\n{r.stdout}{r.stderr}exit {r.returncode}\n"
        ok = r.returncode == 0 and os.path.isdir(trace) and "disconnected" not in r.stdout
        if not ok:
            failed = os.path.join(where, f"attempt-{attempt}")
            os.makedirs(failed, exist_ok=True)
            open(os.path.join(failed, "xctrace.log"), "w").write(log)
            shutil.rmtree(trace, ignore_errors=True)
            clean_tmp()
            continue
        open(os.path.join(where, "xctrace.log"), "w").write(log)
        for table in TABLES[template]:
            x = subprocess.run(["xcrun", "xctrace", "export", "--input", trace, "--xpath",
                                f'/trace-toc/run[@number="1"]/data/table[@schema="{table}"]'], capture_output=True, text=True).stdout
            open(os.path.join(where, f"{table}.xml"), "w").write(x)
        open(os.path.join(where, "trace.sha256"), "w").write(f"{tree_sha256(trace)}  {os.path.basename(trace)}\n")
        if not os.environ.get("KEEP_TRACES"):
            shutil.rmtree(trace)
        clean_tmp()
        return True
    return False
