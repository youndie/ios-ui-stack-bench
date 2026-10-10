#!/bin/sh
# Arm A's Swift filter against fixtures/filter-vectors.json (B-07). The Kotlin half is
# shared/src/iosTest/.../FilterVectorTest.kt; both read the same vector, so the two filters agree on
# every query the study types. Compiles A's own SwiftCatalog.swift for macOS - no simulator needed.
set -eu
ROOT=$(cd "$(dirname "$0")/.." && pwd)
OUT=${TMPDIR:-/tmp}/filter-vectors-$$
xcrun swiftc -O -o "$OUT" \
    "$ROOT/apps/a-native/iosApp/SwiftCatalog.swift" \
    "$ROOT/apps/common/ListUI/ListModel.swift" \
    "$ROOT/scripts/filter-vectors/BenchStub.swift" \
    "$ROOT/scripts/filter-vectors/main.swift"
"$OUT" "$ROOT"
rm -f "$OUT"
