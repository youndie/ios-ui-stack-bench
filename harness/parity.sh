#!/bin/sh
# The first screen of each arm for the parity check (B-27): geometry and a screenshot per arm.
#
#   harness/parity.sh <out-dir> [arm ...]
#
# Writes <out>/<arm>.txt (the PARITY lines) and <out>/<arm>.png (the screenshot, exported from the
# test result). DESTINATION as in harness/run.sh. On a simulator the output is a development check and
# is refused under logs/; B-11 runs it on the devices.
set -eu
ROOT=$(cd "$(dirname "$0")/.." && pwd)
out=$1; shift
case $(mkdir -p "$out" && cd "$out" && pwd) in "$ROOT"/logs/*)
    [ -n "${BENCH_DEVICE:-}" ] || { echo "refusing to write simulator output under logs/" >&2; exit 2; } ;;
esac
DESTINATION=${DESTINATION:-"platform=iOS Simulator,id=$(xcrun simctl list devices booted -j | python3 -c 'import json,sys; print([d["udid"] for r in json.load(sys.stdin)["devices"].values() for d in r if d["state"]=="Booted"][0])')"}
DERIVED=${DERIVED_DATA:-$ROOT/build/DerivedData}/harness
# A device destination signs the runner with the Personal Team of harness/Configuration/Local.xcconfig
# and lets automatic signing register what it needs (B-04); a simulator needs no signing.
case $DESTINATION in id=*) SIGNING="-allowProvisioningUpdates"; DERIVED="$DERIVED-device" ;; *) SIGNING="" ;; esac
python3 "$ROOT/harness/generate_project.py" --check >/dev/null
xcodebuild build-for-testing -project "$ROOT/harness/Harness.xcodeproj" -scheme HarnessUITests \
    -destination "$DESTINATION" -derivedDataPath "$DERIVED" $SIGNING >"$DERIVED.build.log" 2>&1 \
    || { echo "harness build failed - $DERIVED.build.log" >&2; exit 1; }
for arm in ${*:-a-native b1-objc b2-skie b3-swift-export c-kmp-cmp}; do
    case $arm in a-native) b=a ;; b1-objc) b=b1 ;; b2-skie) b=b2 ;; b3-swift-export) b=b3 ;; c-kmp-cmp) b=c ;; esac
    result="$out/$arm.xcresult"; rm -rf "$result"
    TEST_RUNNER_BENCH_BUNDLE="io.github.youndie.iosbench.$b" xcodebuild test-without-building \
        -project "$ROOT/harness/Harness.xcodeproj" -scheme HarnessUITests -destination "$DESTINATION" \
        -derivedDataPath "$DERIVED" -resultBundlePath "$result" -only-testing:HarnessUITests/Parity/testFirstScreen 2>&1 \
        | sed -n 's/.*PARITY //p' > "$out/$arm.txt"
    rm -rf "$out/$arm.attachments"
    xcrun xcresulttool export attachments --path "$result" --output-path "$out/$arm.attachments" >/dev/null
    png=$(find "$out/$arm.attachments" -name '*.png' | head -1)
    [ -n "$png" ] && cp "$png" "$out/$arm.png"
    echo "$arm: $(tr '\n' ' ' < "$out/$arm.txt")$( [ -f "$out/$arm.png" ] && echo '+ screenshot' || echo '- NO screenshot')"
done
