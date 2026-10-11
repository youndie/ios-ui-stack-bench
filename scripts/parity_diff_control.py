#!/usr/bin/env python3
"""parity_diff.py on images whose answer is known (B-27). `make check` runs it.

The images are built here, encoded with every PNG row filter (0-4) so the decoder's unfiltering is
exercised, decoded back, and compared.
"""
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parity_diff as pd  # noqa: E402


def encode(width, height, pixel, alpha=False):
    bpp = 4 if alpha else 3
    raw, prev = bytearray(), bytearray(width * bpp)
    for y in range(height):
        line = bytearray()
        for x in range(width):
            line += bytes(pixel(x, y)) + (b"\xff" if alpha else b"")
        kind = y % 5
        out = bytearray()
        for i in range(len(line)):
            a = line[i - bpp] if i >= bpp else 0
            b = prev[i]
            c = prev[i - bpp] if i >= bpp else 0
            if kind == 0:
                f = line[i]
            elif kind == 1:
                f = line[i] - a
            elif kind == 2:
                f = line[i] - b
            elif kind == 3:
                f = line[i] - ((a + b) >> 1)
            else:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                f = line[i] - (a if pa <= pb and pa <= pc else b if pb <= pc else c)
            out.append(f & 255)
        raw += bytes([kind]) + out
        prev = line

    def chunk(kind, body):
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6 if alpha else 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(raw))) + chunk(b"IEND", b""))


base = lambda x, y: ((x * 7) % 256, (y * 13) % 256, ((x + y) * 3) % 256)
patched = lambda x, y: (255, 0, 0) if 10 <= x < 20 and 30 <= y < 40 else base(x, y)  # 100 px of 40 x 50
faint = lambda x, y: tuple(min(255, v + 10) for v in base(x, y))

A = pd.decode(encode(40, 50, base))
CASES = [
    # Every row against the source pixels: rows use filters 0-4 in turn (y % 5), so each filter is
    # checked. Comparing two decodes with each other would not do - the same wrong decoder agrees with itself.
    ("decoding every filter type gives back every pixel",
     A[2] == [b"".join(bytes(base(x, y)) for x in range(40)) for y in range(50)]),
    ("RGBA decodes to the same RGB", pd.decode(encode(40, 50, base, alpha=True))[2] == A[2]),
    ("an image against itself: 0", pd.differing_share(A, A, 0, 50, 32) == 0),
    ("a 10 x 10 patch in a 40 x 50 image: 100 of 2000 pixels = 5 %",
     abs(pd.differing_share(A, pd.decode(encode(40, 50, patched)), 0, 50, 32) - 0.05) < 1e-9),
    ("the patch outside the band is not counted", pd.differing_share(A, pd.decode(encode(40, 50, patched)), 40, 50, 32) == 0),
    ("a change of 10 per channel is under a delta of 32", pd.differing_share(A, pd.decode(encode(40, 50, faint)), 0, 50, 32) == 0),
]


def main():
    failed = 0
    for name, result in CASES:
        failed += not result
        if "-v" in sys.argv[1:] or not result:
            print(f"  {'ok  ' if result else 'FAIL'} {name}")
    print(f"control for parity_diff.py: {len(CASES) - failed}/{len(CASES)} cases behave")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
