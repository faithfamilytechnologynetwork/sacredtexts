"""Build ``gita_stotrasamhita.json``: every verse of the Bhagavad Gita from Stotra Samhita.

The upstream file ``gita.tex`` is LaTeX for a printed book, so the committed payload is a
filtered extract: the 700 verses only, each half-verse EXACTLY as stored. No preface, chapter
titles, speaker lines, colophons or LaTeX survive. Nothing is cleaned here; the converter
(``sacredbench.convert.convert_stotrasamhita_gita``) owns that.

Usage, with ``gita.tex`` from github.com/stotrasamhita/gita at the commit named below:

    python3 -I texts/raw/Hinduism/build_extract.py <gita.tex> texts/raw/Hinduism/gita_stotrasamhita.json

Shape of the real data (derived from it, commit b89199c, 2026-10-22):

- ``\\chapt{...}`` opens each of 18 chapters.
- A verse is ``\\twolineshloka`` (two half-verses), ``\\fourlineindentedshloka`` (four padas) or
  ``\\onelineshloka``, one ``{...}`` argument per line, closed by a comment ``% .. C-V``.
- ``\\onelineshloka*`` is a half-verse with no number: it joins the next numbered half-verse.
  A speaker line falls inside verses 1.21 and 1.28, which are set this way.
- The verse "prakṛtiṃ puruṣaṃ caiva ..." is commented out as ``13-0`` and upstream's chapter 13
  comments run 13-2..13-35. The number is recorded as stored; the converter renumbers.

Fail-fast: an unexpected line, a comment naming the wrong chapter, a gap in the numbering, or a
chapter whose verse count is not the Gita Press count raises.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

COMMIT = "b89199ce6e8b6648af7f5d6b39085935aa921975"
SHA256 = "06f768a0d9943bebdc773200f22f174e84597b4e7466e14bfb56bdd62b5d567c"
CHAPTER_VERSES = (47, 72, 43, 42, 29, 47, 30, 28, 34, 42, 55, 20, 34, 27, 20, 24, 28, 78)

_MACRO_RE = re.compile(r"\\(twolineshloka|fourlineindentedshloka|onelineshloka)(\*?)$")
_ARG_RE = re.compile(r"\{(.*)\}\s*(?:%\s*\.\.\s*(\d+)-(\d+)\s*(?:\.\.|\\\\)?\s*)?$")


def parse(tex: str) -> list[dict]:
    verses: list[dict] = []
    chapter, in_macro, starred = 0, False, False
    pending: list[str] = []
    for n, raw in enumerate(tex.split("\n"), 1):
        line = raw.strip()
        if not line:
            in_macro = False
        elif line.startswith("%") or line.startswith("\\uvacha"):
            continue
        elif line.startswith("\\chapt"):
            chapter += 1
        elif m := _MACRO_RE.match(line):
            in_macro, starred = True, bool(m.group(2))
        elif line.startswith("{॥"):  # chapter colophon
            continue
        elif in_macro and (m := _ARG_RE.match(line)):
            pending.append(m.group(1))
            if m.group(2):
                if int(m.group(2)) != chapter:
                    raise SystemExit(f"line {n}: comment names chapter {m.group(2)} inside {chapter}")
                verses.append({"chapter": chapter, "number": int(m.group(3)), "lines": pending})
                pending = []
        else:
            raise SystemExit(f"line {n}: unexpected {line!r}")
    if pending:
        raise SystemExit(f"half-verses after the last numbered verse: {pending}")
    for c, want in enumerate(CHAPTER_VERSES, 1):
        got = [v["number"] for v in verses if v["chapter"] == c]
        first = 2 if c == 13 else 1
        if got != list(range(first, first + want)):
            raise SystemExit(f"chapter {c}: expected {want} verses from {first}, got {got[:3]}..{got[-3:]}")
    return verses


def build(tex_path: Path) -> dict:
    body = tex_path.read_bytes()
    digest = hashlib.sha256(body).hexdigest()
    if digest != SHA256:
        raise SystemExit(f"{tex_path}: sha256 {digest} is not gita.tex at {COMMIT}")
    return {
        "upstream": {
            "repo": "https://github.com/stotrasamhita/gita",
            "commit": COMMIT,
            "path": "gita.tex",
            "sha256": SHA256,
            "note": "verbatim half-verses; verses only; number as in upstream's comments",
        },
        "verses": parse(body.decode("utf-8")),
    }


def dump(extract: dict) -> str:
    """One line per verse, so a diff shows exactly which verses changed."""
    head = {k: v for k, v in extract.items() if k != "verses"}
    body = ",\n".join("    " + json.dumps(r, ensure_ascii=False) for r in extract["verses"])
    head_json = json.dumps(head, ensure_ascii=False, indent=2)
    return head_json[:-2] + ',\n  "verses": [\n' + body + "\n  ]\n}\n"


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    extract = build(Path(sys.argv[1]))
    Path(sys.argv[2]).write_text(dump(extract), encoding="utf-8")
    print(f"{len(extract['verses'])} verses, commit {COMMIT}")
