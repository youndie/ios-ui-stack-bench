#!/bin/sh
# Run one scenario against one arm, through the harness's UI tests (B-13).
#
#   harness/run.sh <arm> <S1|S2|S3|S4> [launch arguments...]
#   harness/run.sh c-kmp-cmp S2 -benchStallMs 50
#
# The arm must be installed (scripts/build-arms.sh, then scripts/sim-smoke.sh or a device install).
# DESTINATION defaults to the booted simulator; a device session passes its own. The harness is built
# once per checkout state (build-for-testing) and run without rebuilding, so a scenario run does not
# share the machine with a compiler.
set -eu
ROOT=$(cd "$(dirname "$0")/.." && pwd)
arm=$1; scenario=$2; shift 2
case $scenario in
    S1) test=testS1ColdStart ;; S2) test=testS2Fling ;; S3) test=testS3Filter ;; S4) test=testS4NavigationChurn ;;
    *) echo "unknown scenario $scenario" >&2; exit 2 ;;
esac
case $arm in
    a-native) bundle=a ;; b1-objc) bundle=b1 ;; b2-skie) bundle=b2 ;; b3-swift-export) bundle=b3 ;; c-kmp-cmp) bundle=c ;;
    *) echo "unknown arm $arm" >&2; exit 2 ;;
esac
DESTINATION=${DESTINATION:-"platform=iOS Simulator,id=$(xcrun simctl list devices booted -j | python3 -c 'import json,sys; print([d["udid"] for r in json.load(sys.stdin)["devices"].values() for d in r if d["state"]=="Booted"][0])')"}
DERIVED=${DERIVED_DATA:-$ROOT/build/DerivedData}/harness
# A device destination signs the runner with the Personal Team of harness/Configuration/Local.xcconfig
# and lets automatic signing register what it needs (B-04); a simulator needs no signing.
case $DESTINATION in id=*) SIGNING="-allowProvisioningUpdates"; DERIVED="$DERIVED-device" ;; *) SIGNING="" ;; esac

python3 "$ROOT/harness/generate_project.py" --check >/dev/null
if [ ! -d "$DERIVED/Build/Products" ] || [ -n "${REBUILD:-}" ]; then
    xcodebuild build-for-testing -project "$ROOT/harness/Harness.xcodeproj" -scheme HarnessUITests \
        -destination "$DESTINATION" -derivedDataPath "$DERIVED" $SIGNING >"$DERIVED.build.log" 2>&1 \
        || { echo "harness build failed - $DERIVED.build.log" >&2; tail -20 "$DERIVED.build.log" >&2; exit 1; }
fi
# On a device the tests run from a copy of the .xctestrun without its DSTROOTPath. With that key,
# xcodebuild installs the runner in the "root" style, which only an internal iOS build accepts ("Root
# install style is not supported on this device", B-04); without it, the runner installs as an app.
TESTS="-project $ROOT/harness/Harness.xcodeproj -scheme HarnessUITests"
case $DESTINATION in id=*)
    cp "$(ls -t "$DERIVED"/Build/Products/HarnessUITests_*.xctestrun | head -1)" "$DERIVED/Build/Products/device.xctestrun"
    plutil -remove TestConfigurations.0.TestTargets.0.DSTROOTPath "$DERIVED/Build/Products/device.xctestrun" >/dev/null 2>&1 || true
    TESTS="-xctestrun $DERIVED/Build/Products/device.xctestrun" ;;
esac
TEST_RUNNER_BENCH_BUNDLE="io.github.youndie.iosbench.$bundle" TEST_RUNNER_BENCH_LAUNCH_ARGS="$*" \
    xcodebuild test-without-building $TESTS \
    -destination "$DESTINATION" -derivedDataPath "$DERIVED" -only-testing:"HarnessUITests/Scenarios/$test" 2>&1 \
    | grep -E "Test Case|error:|failed|passed|\*\* TEST" || true
