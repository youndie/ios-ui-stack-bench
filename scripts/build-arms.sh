#!/bin/sh
# Build every arm in Release for the iOS simulator, unsigned — the development build, and what CI
# runs (B-22). Nothing here is a measurement; device builds are signed and go through the harness.
#
#   scripts/build-arms.sh                 every arm
#   scripts/build-arms.sh a-native c-kmp-cmp
#
# Refuses any Xcode but the pinned build: a green build on another toolchain says nothing about the
# one the study measures with (BRIEF.md, pins).
set -eu

PINNED_XCODE_BUILD=27A266a
ROOT=$(cd "$(dirname "$0")/.." && pwd)
DERIVED=${DERIVED_DATA:-$ROOT/build/DerivedData}

actual=$(xcodebuild -version | awk '/Build version/ {print $3}')
if [ "$actual" != "$PINNED_XCODE_BUILD" ]; then
    echo "Xcode build $actual is not the pinned $PINNED_XCODE_BUILD ($(xcode-select -p)) - refusing to build" >&2
    exit 1
fi
echo "Xcode $(xcodebuild -version | head -1 | awk '{print $2}') ($actual), $(xcrun --sdk iphonesimulator --show-sdk-version) simulator SDK"

python3 "$ROOT/apps/generate_projects.py" --check

arms=${*:-"a-native b1-objc b2-skie b3-swift-export c-kmp-cmp"}
failed=""
klibs=""

# The shared module's compiled library: an unpacked klib directory, digested file by file in path
# order. Every Kotlin arm must link the same bytes (B-07); a flag that differed would show here.
klib_digest() {
    dir="$ROOT/shared/build/classes/kotlin/iosSimulatorArm64/main/klib/shared"
    (cd "$dir" && find . -type f | LC_ALL=C sort | xargs shasum -a 256) | shasum -a 256 | cut -c1-16
}

# What each bridge produces from that klib - a framework, or Swift export's merged static library.
kotlin_binary() {
    case $1 in
        b1-objc) echo "$ROOT"/bridge-objc/build/xcode-frameworks/Release/iphonesimulator*/Shared.framework/Shared ;;
        b2-skie) echo "$ROOT"/bridge-skie/build/xcode-frameworks/Release/iphonesimulator*/Shared.framework/Shared ;;
        b3-swift-export) echo "$ROOT"/bridge-swift-export/build/MergedLibraries/iosSimulator/Release/libShared.a ;;
        c-kmp-cmp) echo "$ROOT"/compose-ui/build/xcode-frameworks/Release/iphonesimulator*/ComposeApp.framework/ComposeApp ;;
    esac
}
for arm in $arms; do
    log="$DERIVED/$arm.log"
    mkdir -p "$DERIVED"
    if xcodebuild -project "$ROOT/apps/$arm/iosApp.xcodeproj" -scheme iosApp -configuration Release \
        -sdk iphonesimulator -destination 'generic/platform=iOS Simulator' \
        -derivedDataPath "$DERIVED/$arm" CODE_SIGNING_ALLOWED=NO build >"$log" 2>&1; then
        echo "$arm: built ($(find "$DERIVED/$arm/Build/Products/Release-iphonesimulator" -maxdepth 1 -name '*.app' -exec basename {} \;))"
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
