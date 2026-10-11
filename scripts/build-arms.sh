#!/bin/sh
# Build every arm in Release for the iOS simulator, unsigned — the development build, and what CI
# runs (B-22). Nothing here is a measurement.
#
#   scripts/build-arms.sh                 every arm
#   scripts/build-arms.sh a-native c-kmp-cmp
#   DEVICE=<udid> scripts/build-arms.sh   signed for that device (B-04): the Personal Team from each
#                                         arm's git-ignored Configuration/Local.xcconfig, automatic
#                                         signing allowed to register the device and the App IDs
#
# Refuses any Xcode but the pinned build: a green build on another toolchain says nothing about the
# one the study measures with (BRIEF.md, pins).
set -eu

PINNED_XCODE_BUILD=27A266a
ROOT=$(cd "$(dirname "$0")/.." && pwd)
if [ -n "${DEVICE:-}" ]; then
    SDK=iphoneos; PLATFORM=iphoneos; KLIB_TARGET=iosArm64; SWIFT_EXPORT_DIR=ios
    DERIVED=${DERIVED_DATA:-$ROOT/build/DerivedData-device}
    DEST="id=$DEVICE"; SIGNING="-allowProvisioningUpdates"
else
    SDK=iphonesimulator; PLATFORM=iphonesimulator; KLIB_TARGET=iosSimulatorArm64; SWIFT_EXPORT_DIR=iosSimulator
    DERIVED=${DERIVED_DATA:-$ROOT/build/DerivedData}
    DEST='generic/platform=iOS Simulator'; SIGNING="CODE_SIGNING_ALLOWED=NO"
fi

actual=$(xcodebuild -version | awk '/Build version/ {print $3}')
if [ "$actual" != "$PINNED_XCODE_BUILD" ]; then
    echo "Xcode build $actual is not the pinned $PINNED_XCODE_BUILD ($(xcode-select -p)) - refusing to build" >&2
    exit 1
fi
echo "Xcode $(xcodebuild -version | head -1 | awk '{print $2}') ($actual), $(xcrun --sdk $SDK --show-sdk-version) $SDK SDK${DEVICE:+, for device $DEVICE}"

python3 "$ROOT/apps/generate_projects.py" --check

arms=${*:-"a-native b1-objc b2-skie b3-swift-export c-kmp-cmp"}
failed=""
klibs=""

# The shared module's compiled library: an unpacked klib directory, digested file by file in path
# order. Every Kotlin arm must link the same bytes (B-07); a flag that differed would show here.
klib_digest() {
    dir="$ROOT/shared/build/classes/kotlin/$KLIB_TARGET/main/klib/shared"
    (cd "$dir" && find . -type f | LC_ALL=C sort | xargs shasum -a 256) | shasum -a 256 | cut -c1-16
}

# What each bridge produces from that klib - a framework, or Swift export's merged static library.
kotlin_binary() {
    case $1 in
        b1-objc) echo "$ROOT"/bridge-objc/build/xcode-frameworks/Release/$PLATFORM*/Shared.framework/Shared ;;
        b2-skie) echo "$ROOT"/bridge-skie/build/xcode-frameworks/Release/$PLATFORM*/Shared.framework/Shared ;;
        b3-swift-export) echo "$ROOT"/bridge-swift-export/build/MergedLibraries/$SWIFT_EXPORT_DIR/Release/libShared.a ;;
        c-kmp-cmp) echo "$ROOT"/compose-ui/build/xcode-frameworks/Release/$PLATFORM*/ComposeApp.framework/ComposeApp ;;
    esac
}
for arm in $arms; do
    log="$DERIVED/$arm.log"
    mkdir -p "$DERIVED"
    if xcodebuild -project "$ROOT/apps/$arm/iosApp.xcodeproj" -scheme iosApp -configuration Release \
        -sdk "$SDK" -destination "$DEST" \
        -derivedDataPath "$DERIVED/$arm" $SIGNING build >"$log" 2>&1; then
        echo "$arm: built ($(find "$DERIVED/$arm/Build/Products/Release-$PLATFORM" -maxdepth 1 -name '*.app' -exec basename {} \;))"
        if [ "$arm" != a-native ]; then
            k=$(klib_digest)
            klibs="$klibs $k"
            echo "    shared klib $k, Kotlin binary $(shasum -a 256 $(kotlin_binary "$arm") | cut -c1-16)"
        fi
    else
        echo "$arm: FAILED - $log"
        grep -E 'error:|\*\* BUILD FAILED' "$log" | head -20 | sed 's/^/    /'
        failed="$failed $arm"
    fi
done
[ -z "$failed" ] || { echo "failed:$failed" >&2; exit 1; }
distinct=$(echo $klibs | tr ' ' '\n' | sort -u | grep -c . || true)
if [ "$distinct" -gt 1 ]; then
    echo "the Kotlin arms linked different builds of the shared module:$klibs" >&2
    exit 1
fi
