#!/bin/sh
# Install every arm built by scripts/build-arms.sh on a booted simulator, launch it with the given
# launch arguments, let it run, and print what its instrumentation logged: which kinds of line, the
# markers in order, the stalls. A development check that the instrumentation works end to end; it
# prints counts, never timings, because simulator numbers are not reported (brief, Methodology).
#
#   scripts/sim-smoke.sh                         every arm, stall injector off
#   STALL_MS=50 scripts/sim-smoke.sh a-native    one arm, a 50 ms stall every second
set -eu

ROOT=$(cd "$(dirname "$0")/.." && pwd)
DERIVED=${DERIVED_DATA:-$ROOT/build/DerivedData}
SIM=${SIM:-booted}
SECONDS_RUN=${SECONDS_RUN:-5}
arms=${*:-"a-native b1-objc b2-skie b3-swift-export c-kmp-cmp"}

for arm in $arms; do
    app=$(find "$DERIVED/$arm/Build/Products/Release-iphonesimulator" -maxdepth 1 -name '*.app' | head -1)
    id=$(/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$app/Info.plist")
    xcrun simctl install "$SIM" "$app"
    xcrun simctl terminate "$SIM" "$id" >/dev/null 2>&1 || true
    data=$(xcrun simctl get_app_container "$SIM" "$id" data)
    rm -rf "$data/Documents/bench"
    if [ -n "${STALL_MS:-}" ]; then
        xcrun simctl launch "$SIM" "$id" -benchStallMs "$STALL_MS" >/dev/null
    else
        xcrun simctl launch "$SIM" "$id" >/dev/null
    fi
    sleep "$SECONDS_RUN"
    xcrun simctl terminate "$SIM" "$id"
    python3 - "$arm" "$data"/Documents/bench/*.ndjson <<'PY'
import json, sys
arm, path = sys.argv[1], sys.argv[2]
lines = [json.loads(line) for line in open(path)]
kinds = {}
for line in lines:
    kinds[line["k"]] = kinds.get(line["k"], 0) + 1
marks = [line["name"] for line in sorted((l for l in lines if l["k"] == "mark"), key=lambda l: l["t"])]
header = next(l for l in lines if l["k"] == "header")
stalls = [l for l in lines if l["k"] == "stall"]
print(f"{arm}: {header['bundle']} - lines {kinds}; markers in time order {marks}; "
      f"stall argument {header['stallMs']}, stalls logged {len(stalls)}")
PY
done
