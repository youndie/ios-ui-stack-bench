#!/usr/bin/env python3
"""linkmap.py against a map whose sums are written down by hand (B-26). `make check` runs it."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import linkmap  # noqa: E402

MAP = """# Path: /x/BenchC.app/BenchC
# Arch: arm64
# Object files:
[  0] linker synthesized
[  1] /dd/iosApp.build/Objects-normal/arm64/Bench.o
[  2] /sdk/usr/lib/libSystem.tbd
[  3] /dd/Release-iphoneos/ComposeApp.framework/ComposeApp(ComposeApp.framework.o)
[  4] /dd/Release-iphoneos/ComposeApp.framework/ComposeApp(SkCanvas.o)
[  5] /toolchain/libclang_rt.ios.a(os_version_check.c.o)
# Sections:
# Address\tSize    \tSegment\tSection
0x100004000\t0x00001000\t__TEXT\t__text
0x100010000\t0x00001000\t__DATA\t__bss
# Symbols:
# Address\tSize    \tFile  Name
0x100000000\t0x00000010\t[  0] __mh_execute_header
0x100004000\t0x00000100\t[  1] _bench_start
0x100004100\t0x00000200\t[  1] _bench_mark
0x100004300\t0x00001000\t[  3] _kfun:main
0x100005300\t0x00000800\t[  4] _SkCanvas_draw
0x100005B00\t0x00000020\t[  5] ___isOSVersionAtLeast
0x100005B20\t0x00000000\t[  2] _malloc
0x100010000\t0x00000400\t[  3] _kvar:zeroed
# Dead Stripped Symbols:
#        \tSize    \tFile  Name
<<dead>>\t0x00009999\t[  3] _kfun:unused
""".splitlines()

EXPECTED = {"linker": 0x10, "app": 0x300, "kotlin": 0x1000, "native-in-kotlin": 0x800, "other": 0x20, "system": 0}


CATEGORIES = [
    ("/Users/x/repo/logs/b-12/work/b3-1/dd/Build/Intermediates.noindex/ArchiveIntermediates/iosApp/BuildProductsPath/"
     "Release-iphoneos/libShared.a(Shared.swift.o)", "swift-export"),
    ("/Users/x/repo/build/size-dev/work/b3-1/dd/Build/Products/Release-iphoneos/libShared.a(Shared.swift.o)", "swift-export"),
    ("/Users/x/repo/logs/b-12/work/b3-1/dd/BuildProductsPath/Release-iphoneos/libShared.a(SwiftExportBinary.o)", "kotlin"),
    ("/Users/x/repo/logs/b-12/work/b3-1/dd/BuildProductsPath/Release-iphoneos/libShared.a(mimalloc.cpp.o)", "native-in-kotlin"),
    ("/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/clang/21/lib/darwin/"
     "libclang_rt.ios.a(os_version_check.c.o)", "other"),
]


def main():
    _, sizes = linkmap.parse(MAP)
    wrong = [(p, c, linkmap.category(p)) for p, c in CATEGORIES if linkmap.category(p) != c]
    for p, c, got in wrong:
        print(f"  FAIL {p[-60:]}: {got}, expected {c}")
    ok = sizes == EXPECTED and not wrong
    print(("" if ok else f"  FAIL got {sizes}, expected {EXPECTED}\n") + f"control for linkmap.py: {'1/1' if ok else '0/1'} cases behave")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
