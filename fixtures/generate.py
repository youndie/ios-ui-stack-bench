#!/usr/bin/env python3
"""Generate the study's fixture: 2,000 items, 50 thumbnails, and the filter test vector.

Every arm parses the same bytes and draws the same images, so the bytes are produced here, from a
fixed seed, by a script anybody can rerun — and committed with their digests (BRIEF.md, pins).
Running it twice gives identical files; `--check` says whether the committed files are what it
produces. Pure standard library: the PNG writer is twenty lines of zlib.

    python3 fixtures/generate.py           write the files and print their sha256
    python3 fixtures/generate.py --check   fail if a committed file differs from the output

Outputs:
    apps/common/Fixture/items.json            the fixture every arm bundles (~1 MB)
    apps/common/Thumbnails/drawable/*.png     50 images, 400 x 400 px, every arm bundles - the SwiftUI
                                              arms as bundle files, arm C as Compose resources (the
                                              `drawable/` level is what Compose's resources expect)
    fixtures/filter-vectors.json              query -> expected ids, held against both filters

The filter the vector encodes is the one both implementations claim: a case-insensitive substring
of the title, the query trimmed, a blank query showing every item in fixture order. Titles are ASCII
on purpose, so that Kotlin's `contains(ignoreCase = true)`, Swift's `.caseInsensitive` and Python's
`lower()` cannot disagree for a reason that is not the filter.
"""
import hashlib
import json
import os
import random
import struct
import sys
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURE_DIR = os.path.join(ROOT, "apps", "common", "Fixture")
THUMBNAIL_DIR = os.path.join(ROOT, "apps", "common", "Thumbnails", "drawable")
VECTORS = os.path.join(ROOT, "fixtures", "filter-vectors.json")
SEED = 20261010
ITEMS = 2000
THUMBNAILS = 50
THUMB_PX = 400

ADJECTIVES = ["amber", "brisk", "calm", "dusky", "early", "faint", "gentle", "hollow", "ivory", "jolly",
              "keen", "lunar", "misty", "noble", "olive", "pale", "quiet", "rapid", "silver", "tidal",
              "upper", "vivid", "woven", "young", "zesty"]
NOUNS = ["harbor", "meadow", "river", "summit", "canyon", "forest", "garden", "island", "lagoon", "valley",
         "beacon", "bridge", "castle", "delta", "estate", "fjord", "grove", "haven", "inlet", "jetty"]
WORDS = ("the of and a to in is was that for on are as with his they at be this from have or one had by "
         "word but not what all were we when your can said there use an each which she do how their if will "
         "up other about out many then them these so some her would make like him into time has look two more "
         "write go see number no way could people my than first water been call who oil its now find long down "
         "day did get come made may part").split()
# The S3 scenario types this, one key at a time (B-13); every prefix is in the vector.
S3_QUERY = "amber harbor"


def sentence(rng, words):
    text = " ".join(rng.choice(WORDS) for _ in range(words))
    return text[0].upper() + text[1:] + "."


def items(rng):
    out = []
    for i in range(1, ITEMS + 1):
        out.append({
            "id": i,
            "title": f"{rng.choice(ADJECTIVES).capitalize()} {rng.choice(NOUNS)} {i}",
            "subtitle": sentence(rng, 5),
            "detail": sentence(rng, 9),
            "paragraphs": [sentence(rng, rng.randint(6, 9)) for _ in range(10)],
            "badge": rng.randint(0, 99),
            "thumbnail": rng.randrange(THUMBNAILS),
        })
    return out


def items_json(data):
    # One item per line: a diff of the fixture is readable, and the size stays near the brief's ~1 MB.
    return ("[\n" + ",\n".join(json.dumps(item, separators=(",", ":")) for item in data) + "\n]\n").encode()


def png(width, height, pixel):
    raw = bytearray()
    for y in range(height):
        raw.append(0)  # filter type 0
        for x in range(width):
            raw.extend(pixel(x, y))

    def chunk(kind, body):
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def thumbnail(rng):
    a = [rng.randint(40, 230) for _ in range(3)]
    b = [rng.randint(40, 230) for _ in range(3)]
    cx, cy, r = rng.randint(100, 300), rng.randint(100, 300), rng.randint(60, 140)
    dot = [rng.randint(0, 255) for _ in range(3)]

    def pixel(x, y):
        if (x - cx) ** 2 + (y - cy) ** 2 < r * r:
            return dot
        t = (x + y) / (2 * THUMB_PX)
        return [int(a[k] + (b[k] - a[k]) * t) for k in range(3)]

    return png(THUMB_PX, THUMB_PX, pixel)


def vectors(data):
    queries = [S3_QUERY[:n] for n in range(1, len(S3_QUERY) + 1)] + ["", "   ", "HARBOR", "Harbor 1", "zzz", " lunar "]
    out = []
    for q in queries:
        needle = q.strip().lower()
        ids = [item["id"] for item in data if needle in item["title"].lower()] if needle else [item["id"] for item in data]
        out.append({"query": q, "ids": ids})
    return (json.dumps({"filter": "case-insensitive substring of the title; trimmed; blank shows all",
                        "vectors": out}, separators=(",", ":")) + "\n").encode()


def outputs():
    rng = random.Random(SEED)
    data = items(rng)
    files = {os.path.join(FIXTURE_DIR, "items.json"): items_json(data)}
    for n in range(THUMBNAILS):
        files[os.path.join(THUMBNAIL_DIR, f"thumb-{n:02d}.png")] = thumbnail(rng)
    files[VECTORS] = vectors(data)
    return files


def main():
    check = "--check" in sys.argv[1:]
    stale = []
    for path, data in outputs().items():
        rel = os.path.relpath(path, ROOT)
        if check:
            try:
                current = open(path, "rb").read()
            except FileNotFoundError:
                current = None
            if current != data:
                stale.append(rel)
            continue
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
        print(f"{hashlib.sha256(data).hexdigest()}  {len(data):>9}  {rel}")
    if stale:
        print("stale fixture files - run python3 fixtures/generate.py:\n  " + "\n  ".join(stale))
        return 1
    if check:
        print("fixture files match the generator")
    return 0


if __name__ == "__main__":
    sys.exit(main())
