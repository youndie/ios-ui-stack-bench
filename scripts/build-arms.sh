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
for arm in $arms; do
    log="$DERIVED/$arm.log"
    mkdir -p "$DERIVED"
    if xcodebuild -project "$ROOT/apps/$arm/iosApp.xcodeproj" -scheme iosApp -configuration Release \
        -sdk iphonesimulator -destination 'generic/platform=iOS Simulator' \
        -derivedDataPath "$DERIVED/$arm" CODE_SIGNING_ALLOWED=NO build >"$log" 2>&1; then
        echo "$arm: built ($(find "$DERIVED/$arm/Build/Products/Release-iphonesimulator" -maxdepth 1 -name '*.app' -exec basename {} \;))"
    else
        echo "$arm: FAILED - $log"
        grep -E 'error:|\*\* BUILD FAILED' "$log" | head -20 | sed 's/^/    /'
        failed="$failed $arm"
    fi
done
[ -z "$failed" ] || { echo "failed:$failed" >&2; exit 1; }
