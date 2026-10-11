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
# A device runs from a copy of the .xctestrun without DSTROOTPath, as in harness/run.sh (B-04).
TESTS="-project $ROOT/harness/Harness.xcodeproj -scheme HarnessUITests"
case $DESTINATION in id=*)
    cp "$(ls -t "$DERIVED"/Build/Products/HarnessUITests_*.xctestrun | head -1)" "$DERIVED/Build/Products/device.xctestrun"
    plutil -remove TestConfigurations.0.TestTargets.0.DSTROOTPath "$DERIVED/Build/Products/device.xctestrun" >/dev/null 2>&1 || true
    TESTS="-xctestrun $DERIVED/Build/Products/device.xctestrun" ;;
esac
# On a device the arms take their turns: a free account holds the runner and two arms (B-04), so each
# arm is installed from build/DerivedData-device just before its screen is taken, and the other arms
# are removed. `header.txt` records the stand (logs/README.md).
case $DESTINATION in id=*)
    udid=${DESTINATION#id=}
    { echo "commit $(git -C "$ROOT" rev-parse HEAD)"; xcodebuild -version | tr '\n' ' '; echo
      j=$(mktemp); xcrun devicectl device info details --device "$udid" -j "$j" -q >/dev/null 2>&1
      python3 -c 'import json,sys; r=json.load(open(sys.argv[1]))["result"]; h,d=r["hardwareProperties"],r["deviceProperties"]; print(h["marketingName"], h["productType"], "iOS", d["osVersionNumber"], d["osBuildUpdate"])' "$j"; rm -f "$j"
      date -u +%Y-%m-%dT%H:%M:%SZ; } > "$out/header.txt" ;;
esac
for arm in ${*:-a-native b1-objc b2-skie b3-swift-export c-kmp-cmp}; do
    case $arm in a-native) b=a ;; b1-objc) b=b1 ;; b2-skie) b=b2 ;; b3-swift-export) b=b3 ;; c-kmp-cmp) b=c ;; esac
    case $DESTINATION in id=*)
        for other in a b1 b2 b3 c; do
            [ "$other" = "$b" ] || xcrun devicectl device uninstall app --device "$udid" "io.github.youndie.iosbench.$other" >/dev/null 2>&1 || true
        done
        app=$(ls -d "$ROOT"/build/DerivedData-device/$arm/Build/Products/Release-iphoneos/*.app)
        xcrun devicectl device install app --device "$udid" "$app" >/dev/null
        echo "$arm $(shasum -a 256 "$app/$(plutil -extract CFBundleExecutable raw "$app/Info.plist")" | cut -d' ' -f1)" >> "$out/header.txt" ;;
    esac
    result="$out/$arm.xcresult"; rm -rf "$result"
    TEST_RUNNER_BENCH_BUNDLE="io.github.youndie.iosbench.$b" xcodebuild test-without-building \
        $TESTS -destination "$DESTINATION" \
        -derivedDataPath "$DERIVED" -resultBundlePath "$result" -only-testing:HarnessUITests/Parity/testFirstScreen \
        > "$out/$arm.log" 2>&1 || true
    sed -n 's/.*PARITY //p' "$out/$arm.log" > "$out/$arm.txt"
    rm -rf "$out/$arm.attachments"
    xcrun xcresulttool export attachments --path "$result" --output-path "$out/$arm.attachments" >/dev/null
    png=$(find "$out/$arm.attachments" -name '*.png' | head -1)
    [ -n "$png" ] && cp "$png" "$out/$arm.png"
    echo "$arm: $(tr '\n' ' ' < "$out/$arm.txt")$( [ -f "$out/$arm.png" ] && echo '+ screenshot' || echo '- NO screenshot')"
done
