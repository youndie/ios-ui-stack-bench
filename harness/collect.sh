#!/bin/sh
# Run one scenario against one arm and turn the app's log into CSVs (B-14).
#
#   harness/collect.sh <arm> <S1|S2|S3|S4> <out-dir> [launch arguments...]
#
# On the simulator - the only target this script drives today - the output is a development check
# and is refused under logs/: simulator numbers are never reported (brief, Methodology). The device
# path, and the xctrace recording beside the app's log, are B-24's: Instruments records no hitches on
# a simulator, and its App Launch recording hangs there (research §1.12).
set -eu
ROOT=$(cd "$(dirname "$0")/.." && pwd)
arm=$1; scenario=$2; out=$3; shift 3
case $(cd "$(dirname "$out")" 2>/dev/null && pwd)/$(basename "$out") in
    "$ROOT"/logs/*) echo "refusing to write simulator output under logs/ - $out" >&2; exit 2 ;;
esac
case $arm in
    a-native) bundle=a ;; b1-objc) bundle=b1 ;; b2-skie) bundle=b2 ;; b3-swift-export) bundle=b3 ;; c-kmp-cmp) bundle=c ;;
    *) echo "unknown arm $arm" >&2; exit 2 ;;
esac
id=io.github.youndie.iosbench.$bundle
data=$(xcrun simctl get_app_container booted "$id" data)
rm -rf "$data/Documents/bench"
"$ROOT/harness/run.sh" "$arm" "$scenario" "$@" | grep -E 'passed \(|failed \(' || true
logs=$(ls "$data"/Documents/bench/*.ndjson 2>/dev/null | wc -l | tr -d ' ')
[ "$logs" = 1 ] || { echo "expected one log from one launch, found $logs" >&2; exit 1; }
mkdir -p "$out"
cp "$data"/Documents/bench/*.ndjson "$out/app.ndjson"
python3 "$ROOT/analysis/inapp_reader.py" "$out/app.ndjson" --scenario "$scenario" --out "$out"
