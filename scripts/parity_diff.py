#!/usr/bin/env python3
"""The share of differing pixels between two first-screen screenshots, over a region (B-27, for B-11).

    python3 scripts/parity_diff.py <a.png> <b.png> --top <pt> --bottom <pt> [--scale 3] [--delta 32]

The region is a horizontal band in points - from the first row's top to the last visible row's
bottom, as `harness/parity.sh` reports them - turned into pixels by the screen scale, full width,
with the system chrome outside it (A1.4, I12). A pixel differs when any channel differs by more than
`--delta` (0-255); the result is the share of differing pixels in the band. The tolerance it is held
against is B-11's, fixed before its first diff; this script decides nothing.

Standard library only: an 8-bit RGB / RGBA PNG decoder (all five filter types, no interlace) is
below, because a reader that cannot be checked against its own control is not one.
"""
import argparse
import struct
import sys
import zlib


def decode(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    i, idat, header = 8, b"", None
    while i < len(data):
        n, kind = struct.unpack(">I4s", data[i:i + 8])
        body = data[i + 8:i + 8 + n]
        if kind == b"IHDR":
            header = struct.unpack(">IIBBBBB", body)
        elif kind == b"IDAT":
            idat += body
        i += 12 + n
    width, height, depth, color, _, _, interlace = header
    if depth != 8 or color not in (2, 6) or interlace:
        raise ValueError(f"unsupported PNG: depth {depth}, colour type {color}, interlace {interlace}")
    bpp = 3 if color == 2 else 4
    raw, stride = zlib.decompress(idat), width * (3 if color == 2 else 4)
    rows, prev, pos = [], bytearray(stride), 0
    for _ in range(height):
        kind, line = raw[pos], bytearray(raw[pos + 1:pos + 1 + stride])
        pos += 1 + stride
        for x in range(stride):
            a = line[x - bpp] if x >= bpp else 0
            b = prev[x]
            c = prev[x - bpp] if x >= bpp else 0
            if kind == 1:
                line[x] = (line[x] + a) & 255
            elif kind == 2:
                line[x] = (line[x] + b) & 255
            elif kind == 3:
                line[x] = (line[x] + ((a + b) >> 1)) & 255
            elif kind == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append(bytes(line) if bpp == 3 else bytes(v for k, v in enumerate(line) if k % 4 != 3))
        prev = line
    return width, height, rows


def differing_share(a, b, top_px, bottom_px, delta):
    (wa, ha, ra), (wb, hb, rb) = a, b
    if (wa, ha) != (wb, hb):
        raise ValueError(f"different sizes: {wa}x{ha} and {wb}x{hb}")
    top, bottom = max(0, top_px), min(ha, bottom_px)
    differing = total = 0
    for y in range(top, bottom):
        x_row, y_row = ra[y], rb[y]
        for x in range(0, wa * 3, 3):
            total += 1
            if (abs(x_row[x] - y_row[x]) > delta or abs(x_row[x + 1] - y_row[x + 1]) > delta
                    or abs(x_row[x + 2] - y_row[x + 2]) > delta):
                differing += 1
    return differing / total if total else 0.0


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("a")
    p.add_argument("b")
    p.add_argument("--top", type=float, required=True)
    p.add_argument("--bottom", type=float, required=True)
    p.add_argument("--scale", type=float, default=3)
    p.add_argument("--delta", type=int, default=32)
    args = p.parse_args()
    a, b = (decode(open(f, "rb").read()) for f in (args.a, args.b))
    share = differing_share(a, b, int(args.top * args.scale), int(args.bottom * args.scale), args.delta)
    print(f"differing pixels over the band: {100 * share:.3f} %")
    return 0


if __name__ == "__main__":
    sys.exit(main())
