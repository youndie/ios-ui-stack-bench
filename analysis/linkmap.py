#!/usr/bin/env python3
"""Sum an ld link map by where the bytes came from (B-26, research D6).

    python3 analysis/linkmap.py <linkmap.txt>

With a static Kotlin framework there is no Kotlin file in the .app to measure: everything is in the
main executable (research §1.9). The map the linker writes (`LD_GENERATE_MAP_FILE`) names, for every
symbol, the object it came from; summing symbol sizes by that object's origin gives the breakdown.

Categories, by the object's path:
    app              the app's own Swift objects (`Objects-normal/`)
    kotlin           the Kotlin/Native program: the framework's `<Name>.framework.o` member, or the
                     object Swift export links in - Kotlin code, its libraries and the K/N runtime
    native-in-kotlin every other member of the Kotlin framework or library: C, C++ and Objective-C it
                     carries - for arm C, Skia and Skiko and Compose's UIKit glue
    swift-export     Swift export's generated Swift, compiled into the library (arm B3)
    linker           linker-synthesized
    other            anything else with bytes (compiler-rt, ...)
System libraries and frameworks are `.tbd` stubs and contribute nothing.

Symbols in zero-fill sections (`__bss`, `__common`) are left out: they take address space, not file
bytes. The sum is then smaller than the executable - Mach-O headers, LINKEDIT (symbol tables,
fixups) and padding are not symbols - and the remainder is reported, not hidden.
"""
import re
import sys

OBJECT = re.compile(r"^\[\s*(\d+)\]\s+(.*)$")
SYMBOL = re.compile(r"^0x([0-9A-Fa-f]+)\s+0x([0-9A-Fa-f]+)\s+\[\s*(\d+)\]")
SECTION = re.compile(r"^0x([0-9A-Fa-f]+)\s+0x([0-9A-Fa-f]+)\s+(\S+)\s+(\S+)")
# Zero-fill sections occupy address space and no file bytes; their symbols are not counted.
ZEROFILL = {"__bss", "__common", "__thread_bss"}
MEMBER = re.compile(r"\(([^)]+)\)$")


def category(path):
    if path == "linker synthesized":
        return "linker"
    if "/Objects-normal/" in path:
        return "app"
    member = MEMBER.search(path)
    if member:
        name, container = member.group(1), path[: member.start()]
        if name.endswith(".framework.o") or re.search(r"SwiftExportBinary|KotlinProgram", name):
            return "kotlin"
        if ".framework/" in container:
            return "native-in-kotlin"
        if container.endswith(".a") and "/build/" in container:
            return "swift-export" if name.endswith(".o") and not name.endswith(".cpp.o") else "native-in-kotlin"
    if path.endswith((".tbd", ".dylib")):
        return "system"
    return "other"


def parse(lines):
    objects, sizes, section, zerofill = {}, {}, None, []
    for line in lines:
        if line.startswith("# Object files:"):
            section = "objects"
            continue
        if line.startswith("# Sections:"):
            section = "sections"
            continue
        if line.startswith("# Symbols:"):
            section = "symbols"
            continue
        if line.startswith("# Dead Stripped Symbols:"):
            break
        if section == "sections":
            m = SECTION.match(line)
            if m and m.group(4) in ZEROFILL:
                start = int(m.group(1), 16)
                zerofill.append((start, start + int(m.group(2), 16)))
            continue
        if section == "objects":
            m = OBJECT.match(line)
            if m:
                objects[int(m.group(1))] = m.group(2).strip()
        elif section == "symbols":
            m = SYMBOL.match(line)
            if m:
                address = int(m.group(1), 16)
                if any(a <= address < b for a, b in zerofill):
                    continue
                cat = category(objects.get(int(m.group(3)), ""))
                sizes[cat] = sizes.get(cat, 0) + int(m.group(2), 16)
    return objects, sizes


def main():
    with open(sys.argv[1], encoding="utf-8", errors="replace") as f:
        _, sizes = parse(f)
    for cat in sorted(sizes, key=lambda c: -sizes[c]):
        print(f"{cat}\t{sizes[cat]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
