#!/usr/bin/env python3
"""RQ1's size proxy, as the brief defines it, for every arm (B-26; the measurement itself is B-12's).

    python3 scripts/measure_size.py <out-dir> [arm ...]

For each arm, twice from a clean tree: archive for the device SDK with signing disabled (Release,
arm64), then measure the `.app`:
    uncompressed_bytes   the sum of its files' sizes
    compressed_bytes     the size of `zip -9 -r -X` of it - the brief's download proxy
    executable_bytes     the main executable, and its sha256
    map_<category>       the final link map summed by origin (analysis/linkmap.py)
and write `<out>/sizes.csv`, one row per arm and build, in the shape analysis/verdicts.py reads (it
takes `compressed_bytes`; the rows of build 1 are the measurement, build 2 is the determinism check).

"Clean" means a new derived-data directory, the Kotlin modules' build directories deleted, and
Gradle's build cache off, so the second build compiles Kotlin again rather than restoring the first.

The measurement's own control: a copy of each first build's `.app` with one extra file of 1 MiB of
seeded random bytes, measured the same way, must come out about 1 MiB larger compressed.

Refuses `logs/`: writing there closes the amendment window, which is B-12's, with the owner's go.
"""
import csv
import hashlib
import os
import plistlib
import random
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
import linkmap  # noqa: E402

ARMS = ["a-native", "b1-objc", "b2-skie", "b3-swift-export", "c-kmp-cmp"]
KOTLIN_BUILD_DIRS = ["shared", "bridge-objc", "bridge-skie", "bridge-swift-export", "compose-ui"]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tree_bytes(path):
    total = 0
    for base, _, files in os.walk(path):
        for name in files:
            total += os.lstat(os.path.join(base, name)).st_size
    return total


def zipped_bytes(app):
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "app.zip")
        subprocess.run(["zip", "-9", "-r", "-X", "-y", "-q", out, os.path.basename(app)],
                       cwd=os.path.dirname(app), check=True)
        return os.path.getsize(out)


def archive(arm, work):
    for module in KOTLIN_BUILD_DIRS:
        shutil.rmtree(os.path.join(ROOT, module, "build"), ignore_errors=True)
    derived = os.path.join(work, "dd")
    mapfile = os.path.join(work, "linkmap.txt")
    env = dict(os.environ, GRADLE_OPTS="-Dorg.gradle.caching=false")
    log = os.path.join(work, "archive.log")
    with open(log, "w") as f:
        r = subprocess.run(["xcodebuild", "archive", "-project", os.path.join(ROOT, "apps", arm, "iosApp.xcodeproj"),
                            "-scheme", "iosApp", "-configuration", "Release", "-sdk", "iphoneos",
                            "-destination", "generic/platform=iOS", "-archivePath", os.path.join(work, "app.xcarchive"),
                            "-derivedDataPath", derived, "CODE_SIGNING_ALLOWED=NO",
                            "LD_GENERATE_MAP_FILE=YES", f"LD_MAP_FILE_PATH={mapfile}"],
                           stdout=f, stderr=subprocess.STDOUT, env=env)
    if r.returncode != 0:
        raise SystemExit(f"{arm}: archive failed - {log}")
    apps = os.path.join(work, "app.xcarchive", "Products", "Applications")
    return os.path.join(apps, os.listdir(apps)[0]), mapfile


def macho_layout(exe):
    """File bytes in sections, and the __LINKEDIT segment's size, from `otool -l`: what the link map's
    symbols do not cover is LINKEDIT, headers and page padding, and these two columns show it."""
    lines = subprocess.run(["otool", "-l", exe], capture_output=True, text=True, check=True).stdout.split("\n")
    sections, linkedit, cur = 0, 0, {}
    for i, line in enumerate(lines):
        t = line.strip()
        if t == "segname __LINKEDIT":
            for j in range(i, min(i + 8, len(lines))):
                if lines[j].strip().startswith("filesize"):
                    linkedit = int(lines[j].split()[1])
        for key in ("sectname", "size", "offset"):
            if t.startswith(key + " "):
                cur[key] = t.split()[1]
        if t.startswith("reserved2") and "sectname" in cur:
            if int(cur["offset"]) > 0:  # zero-fill sections have no file offset
                sections += int(cur["size"], 16)
            cur = {}
    return sections, linkedit


def measure(arm, build, work):
    app, mapfile = archive(arm, work)
    info = plistlib.load(open(os.path.join(app, "Info.plist"), "rb"))
    exe = os.path.join(app, info["CFBundleExecutable"])
    with open(mapfile, encoding="utf-8", errors="replace") as f:
        _, categories = linkmap.parse(f)
    row = {"arm": arm, "build": build, "uncompressed_bytes": tree_bytes(app), "compressed_bytes": zipped_bytes(app),
           "executable_bytes": os.path.getsize(exe), "executable_sha256": sha256(exe)}
    for cat in ("app", "kotlin", "native-in-kotlin", "swift-export", "linker", "system", "other"):
        row[f"map_{cat}"] = categories.get(cat, 0)
    row["map_remainder"] = row["executable_bytes"] - sum(categories.values())
    row["section_bytes"], row["linkedit_bytes"] = macho_layout(exe)
    return row, app


def control(app):
    """The same app plus 1 MiB of seeded random bytes must zip about 1 MiB larger."""
    with tempfile.TemporaryDirectory() as tmp:
        copy = os.path.join(tmp, os.path.basename(app))
        shutil.copytree(app, copy, symlinks=True)
        before = zipped_bytes(copy)
        with open(os.path.join(copy, "control.bin"), "wb") as f:
            f.write(random.Random(20261010).randbytes(1 << 20))
        return zipped_bytes(copy) - before


def main():
    out = os.path.abspath(sys.argv[1])
    if out.startswith(os.path.join(ROOT, "logs") + os.sep) and not os.environ.get("BENCH_WINDOW_CLOSED"):
        raise SystemExit("refusing logs/: the size measurement closes the amendment window, which is B-12's")
    arms = sys.argv[2:] or ARMS
    os.makedirs(out, exist_ok=True)
    rows = []
    for arm in arms:
        apps = []
        for build in (1, 2):
            work = os.path.join(out, "work", f"{arm}-{build}")
            shutil.rmtree(work, ignore_errors=True)
            os.makedirs(work)
            row, app = measure(arm, build, work)
            rows.append(row)
            apps.append(app)
            print(f"{arm} build {build}: executable {row['executable_sha256'][:16]}")
        same = rows[-1]["executable_sha256"] == rows[-2]["executable_sha256"]
        delta = control(apps[0])
        print(f"{arm}: two clean builds {'identical' if same else 'DIFFER'}; 1 MiB control moved the zip by {delta} bytes")
        rows[-2]["control_1mib_delta"] = rows[-1]["control_1mib_delta"] = delta
        rows[-2]["deterministic"] = rows[-1]["deterministic"] = int(same)
    with open(os.path.join(out, "sizes.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"sizes.csv in {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
