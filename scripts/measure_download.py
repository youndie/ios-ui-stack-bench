#!/usr/bin/env python3
"""RQ1's download size as Apple estimates it, and its worst case under App Store encryption (B-31, A2.4).

    python3 scripts/measure_download.py <out-dir> [arm ...]

For each arm, twice from a clean tree: archive for the device, signed by the Personal Team
(`Local.xcconfig`, `-allowProvisioningUpdates`), then export it as a development build with app
thinning for all variants. That is Apple's own procedure for an app size report ("Reducing your app's
size", developer.apple.com). From the export it reads the thinned variant that serves the iPhone XS
(`iPhone11,2`, iOS 18) in `app-thinning.plist`:

    apple_download_bytes   `sizeCompressedApp`: Apple's estimate of the download - RQ1's proxy
    apple_install_bytes    `sizeUncompressedApp`: the installed size
    payload_zip_bytes      `zip -9` of that variant's unpacked IPA, the B-12 proxy for the same bytes
    worst_case_bytes       the same zip after the main executable's encrypted range (`LC_ENCRYPTION_INFO_64`
                           `cryptoff` / `cryptsize`) is overwritten with seeded random bytes: the App
                           Store encrypts that range after upload, and encrypted bytes do not compress. This is
                           the method of fastlane's store_sizer plugin. It is a bound, not a measurement.
                           Whether a given iOS version downloads it this way is not documented by Apple.
    encrypted_bytes        cryptsize
    executable_sha256      of the exported variant's main executable

and writes `<out>/download.csv`. Refuses `logs/` unless BENCH_WINDOW_CLOSED is set, like
measure_size.py.
"""
import csv
import glob
import hashlib
import os
import plistlib
import random
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARMS = ["a-native", "b1-objc", "b2-skie", "b3-swift-export", "c-kmp-cmp"]
KOTLIN_BUILD_DIRS = ["shared", "bridge-objc", "bridge-skie", "bridge-swift-export", "compose-ui"]
DEVICE, OS_MAJOR = "iPhone11,2", "18"
TEAM = re.search(r"TEAM_ID\s*=\s*(\S+)", open(os.path.join(ROOT, "apps", "a-native", "Configuration", "Local.xcconfig")).read()).group(1)
OPTIONS = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>method</key><string>debugging</string>
<key>thinning</key><string>&lt;thin-for-all-variants&gt;</string>
<key>signingStyle</key><string>automatic</string>
<key>teamID</key><string>{TEAM}</string>
</dict></plist>
"""


def run(cmd, log, **kw):
    with open(log, "w") as f:
        r = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, **kw)
    if r.returncode:
        raise SystemExit(f"{cmd[1]} failed - {log}")


def zip_dir(src, name):
    with tempfile.TemporaryDirectory() as t:
        out = os.path.join(t, "x.zip")
        subprocess.run(["zip", "-9", "-r", "-X", "-y", "-q", out, name], cwd=src, check=True)
        return os.path.getsize(out)


def xs_variant(export):
    info = plistlib.load(open(os.path.join(export, "app-thinning.plist"), "rb"))["variants"]
    for ipa, v in info.items():
        if any(d.get("device") == DEVICE and str(d.get("os-version", "")).split(".")[0] == OS_MAJOR for d in v.get("variantDescriptors", [])):
            return os.path.join(export, ipa), v
    raise SystemExit(f"no thinned variant for {DEVICE} iOS {OS_MAJOR} in {export}")


def measure(arm, build, work):
    for module in KOTLIN_BUILD_DIRS:
        shutil.rmtree(os.path.join(ROOT, module, "build"), ignore_errors=True)
    archive, export = os.path.join(work, "app.xcarchive"), os.path.join(work, "export")
    env = dict(os.environ, GRADLE_OPTS="-Dorg.gradle.caching=false")
    run(["xcodebuild", "archive", "-project", os.path.join(ROOT, "apps", arm, "iosApp.xcodeproj"), "-scheme", "iosApp",
         "-configuration", "Release", "-destination", "generic/platform=iOS", "-archivePath", archive,
         "-derivedDataPath", os.path.join(work, "dd"), "-allowProvisioningUpdates"], os.path.join(work, "archive.log"), env=env)
    opts = os.path.join(work, "export-options.plist")
    open(opts, "w").write(OPTIONS)
    run(["xcodebuild", "-exportArchive", "-archivePath", archive, "-exportPath", export, "-exportOptionsPlist", opts,
         "-allowProvisioningUpdates"], os.path.join(work, "export.log"))
    ipa, variant = xs_variant(export)
    unpacked = os.path.join(work, "unpacked")
    shutil.rmtree(unpacked, ignore_errors=True)
    zipfile.ZipFile(ipa).extractall(unpacked)
    app = glob.glob(os.path.join(unpacked, "Payload", "*.app"))[0]
    exe = os.path.join(app, plistlib.load(open(os.path.join(app, "Info.plist"), "rb"))["CFBundleExecutable"])
    digest = hashlib.sha256(open(exe, "rb").read()).hexdigest()
    plain = zip_dir(unpacked, "Payload")
    lc = subprocess.run(["otool", "-l", exe], capture_output=True, text=True, check=True).stdout
    off, size = int(re.search(r"cryptoff (\d+)", lc).group(1)), int(re.search(r"cryptsize (\d+)", lc).group(1))
    with open(exe, "r+b") as f:
        f.seek(off)
        f.write(random.Random(20261012).randbytes(size))
    worst = zip_dir(unpacked, "Payload")
    return {"arm": arm, "build": build, "apple_download_bytes": variant["sizeCompressedApp"], "apple_install_bytes": variant["sizeUncompressedApp"],
            "payload_zip_bytes": plain, "worst_case_bytes": worst, "encrypted_bytes": size, "executable_sha256": digest,
            "variant": os.path.basename(ipa)}


def main():
    out = os.path.abspath(sys.argv[1])
    if out.startswith(os.path.join(ROOT, "logs") + os.sep) and not os.environ.get("BENCH_WINDOW_CLOSED"):
        raise SystemExit("refusing logs/ without BENCH_WINDOW_CLOSED")
    rows = []
    for arm in sys.argv[2:] or ARMS:
        for build in (1, 2):
            work = os.path.join(out, "work", f"{arm}-{build}")
            shutil.rmtree(work, ignore_errors=True)
            os.makedirs(work)
            row = measure(arm, build, work)
            rows.append(row)
            print(f"{arm} build {build}: Apple {row['apple_download_bytes']}, zip {row['payload_zip_bytes']}, worst case {row['worst_case_bytes']}", flush=True)
    with open(os.path.join(out, "download.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"download.csv in {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
