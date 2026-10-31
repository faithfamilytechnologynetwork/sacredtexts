"""Build ``gita_besant.json``: Annie Besant's English Bhagavad Gita, verse by verse.

The source is the English Wikisource transcription of *The Bhagavad-Gita, with the text in
Devanagari and an English translation*, 4th edition (G. A. Natesan & Co., Madras, October 1922),
proofread against its scan. Wikisource holds one wikitext page per printed page, so this script
pins a revision of each page and expands the wikitext to plain English. Only the translation is
kept: the Devanagari, footnotes, speaker lines, headings and colophons are dropped.

Usage, from the repository root:

    python3 -I texts/raw/Hinduism/build_besant.py fetch  <pages.json> [texts/raw/Hinduism/gita_besant.json]
    python3 -I texts/raw/Hinduism/build_besant.py build  <pages.json> texts/raw/Hinduism/gita_besant.json

``fetch`` downloads the revisions pinned in the extract, or the latest ones if none is given.

Shape of the real data (derived from it, revisions current on 2026-10-30):

- Printed pages 1..264 are djvu pages 11..275. Each verse's English ends in
  ``{{float right|{{larger|(N)}}}}``, so a verse is the text between two markers.
- Six markers are corrected with ``{{SIC|printed|corrected}}``; two more are in ``_MARKER_ERRATA``.
- A word hyphenated at a page end is joined, as Wikisource renders it.
- Besant numbers the verse "prakriti purusha" as 13.1, so her chapter 13 has 35 verses. It is
  kept here; the converter sets it aside.

Fail-fast: an unknown template, unbalanced braces, a verse-number gap, a chapter whose verse
count is not Besant's, or Devanagari or markup left in a verse raises.
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://en.wikisource.org/w/api.php"
INDEX = "Bhagavad Gita - Annie Besant 4th edition.djvu"
FIRST_PAGE, LAST_PAGE = 11, 275
CHAPTER_VERSES = (47, 72, 43, 42, 29, 47, 30, 28, 34, 42, 55, 20, 35, 27, 20, 24, 28, 78)
USER_AGENT = "SacredBench-corpus/0.1 (https://github.com/faithfamilytechnologynetwork/sacredtexts)"

_DROP = {
    "-", "dhr", "nop", "gap", "rule", "custom rule", "parabr", "block center/s", "block center/e",
    "larger block/s", "larger block/e", "fine block", "center",
}
_KEEP_LAST_ARG = {
    "sc", "small-caps", "sp", "larger", "x-larger", "xx-larger", "xxx-larger",
    "block center", "larger block",
}
# English verse markers misprinted in the book, and not flagged in the transcription:
# (chapter, true verse) -> printed number. The adjacent Devanagari carries the true number.
_MARKER_ERRATA = {(17, 19): 20, (18, 14): 15}
_MARK = "\x01"  # stands for a verse marker; never in wikitext
_SPEAKER_RE = re.compile(
    r"^(?:The Blessed Lord|Arjuna|Sanjaya|Dhritarâshtra) said:\s*"
)
_TEMPLATE_RE = re.compile(r"\{\{([^{}]*)\}\}")
_LINK_RE = re.compile(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]")


def _expand_one(m: re.Match) -> str:
    name, *args = m.group(1).split("|")
    name = name.strip()
    if name == "SIC":  # {{SIC|printed|corrected}}, or {{SIC|printed}} for a marked oddity
        return args[-1]
    if name == "float right":
        return _MARK + args[-1].strip("() ") + _MARK
    if name in ("c", "fine block") or name in _DROP:
        return " "
    if name in ("lang", "lang block"):  # always the Devanagari
        return " "
    if name in _KEEP_LAST_ARG:
        return args[-1]
    raise SystemExit(f"unknown template {name!r} in {m.group(0)[:80]!r}")


def page_text(wikitext: str) -> str:
    """One page's wikitext -> plain text with verse markers."""
    t = re.sub(r"<noinclude>.*?</noinclude>", "", wikitext, flags=re.S)
    t = re.sub(r"<ref[^>]*/>", "", t)
    t = re.sub(r"<ref\b[^>]*>.*?</ref>", "", t, flags=re.S)
    t = re.sub(r"</?poem>|<br\s*/?>", " ", t)
    t = _LINK_RE.sub(r"\1", t)
    while True:
        t, n = _TEMPLATE_RE.subn(_expand_one, t)
        if not n:
            break
    if "{{" in t or "}}" in t:
        raise SystemExit(f"unbalanced braces near {t[max(0, t.find('{{') - 40):][:120]!r}")
    return t.replace("''", "").replace("⁠", "")


def parse(pages: dict[str, dict]) -> list[dict]:
    joined = ""
    for n in range(FIRST_PAGE, LAST_PAGE + 1):
        text = page_text(pages[str(n)]["text"])
        tail = text.rstrip()
        if tail.endswith("-") and joined is not None:  # a word broken across the page end
            joined += tail[:-1]
            joined += "\x02"
        else:
            joined += text + " "
    joined = re.sub(r"\x02\s*", "", joined)
    parts = joined.split(_MARK)
    verses: list[dict] = []
    chapter, expected = 0, 1
    used: set[tuple[int, int]] = set()
    for i in range(1, len(parts), 2):
        number = int(parts[i])
        if _MARKER_ERRATA.get((chapter, expected)) == number:
            used.add((chapter, expected))
            number = expected
        if number == 1:
            if chapter and expected - 1 != CHAPTER_VERSES[chapter - 1]:
                raise SystemExit(f"chapter {chapter}: {expected - 1} verses")
            chapter, expected = chapter + 1, 1
        if number != expected:
            raise SystemExit(f"chapter {chapter}: verse {number} where {expected} was expected")
        expected += 1
        text = _SPEAKER_RE.sub("", " ".join(parts[i - 1].split()))
        if not text or re.search(r"[ऀ-ॿ{}|<>=\[\]]|DISCOURSE", text):
            raise SystemExit(f"{chapter}.{number}: bad text {text[:120]!r}")
        verses.append({"chapter": chapter, "number": number, "text": text})
    if chapter != 18 or expected - 1 != CHAPTER_VERSES[-1]:
        raise SystemExit(f"ended at chapter {chapter}, verse {expected - 1}")
    if used != set(_MARKER_ERRATA):
        raise SystemExit(f"stale marker errata: {set(_MARKER_ERRATA) - used}")
    return verses


def _query(params: dict) -> dict:
    url = API + "?" + urllib.parse.urlencode({**params, "format": "json", "formatversion": "2"})
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for _ in range(6):
        try:
            return json.load(urllib.request.urlopen(request))
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(int(e.headers.get("Retry-After") or 30) + 2)
    raise SystemExit("rate limited")


def fetch(pinned: dict[str, int] | None) -> dict[str, dict]:
    numbers = [str(n) for n in range(FIRST_PAGE, LAST_PAGE + 1)]
    pages: dict[str, dict] = {}
    for start in range(0, len(numbers), 20):
        batch = numbers[start : start + 20]
        params = {"action": "query", "prop": "revisions", "rvprop": "ids|content", "rvslots": "main"}
        if pinned:
            params["revids"] = "|".join(str(pinned[n]) for n in batch)
        else:
            params["titles"] = "|".join(f"Page:{INDEX}/{n}" for n in batch)
        for p in _query(params)["query"]["pages"]:
            rv = p["revisions"][0]
            pages[p["title"].rsplit("/", 1)[1]] = {"rev": rv["revid"], "text": rv["slots"]["main"]["content"]}
        time.sleep(4)
    if sorted(pages, key=int) != numbers:
        raise SystemExit("pages missing from the response")
    return pages


def dump(pages: dict[str, dict]) -> str:
    """One line per verse, so a diff shows exactly which verses changed."""
    head = {
        "upstream": {
            "work": "The Bhagavad-Gita, with the text in Devanagari and an English translation",
            "translator": "Annie Besant",
            "edition": "4th edition, G. A. Natesan & Co., Madras, October 1922",
            "transcription": f"https://en.wikisource.org/wiki/Index:{INDEX.replace(' ', '_')}",
            "revisions": {n: pages[n]["rev"] for n in sorted(pages, key=int)},
            "note": "English only; footnotes, speakers, headings and colophons dropped",
        },
    }
    body = ",\n".join("    " + json.dumps(r, ensure_ascii=False) for r in parse(pages))
    return json.dumps(head, ensure_ascii=False, indent=2)[:-2] + ',\n  "verses": [\n' + body + "\n  ]\n}\n"


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("fetch", "build"):
        raise SystemExit(__doc__)
    if sys.argv[1] == "fetch":
        pins = None
        if len(sys.argv) > 3:
            pins = json.loads(Path(sys.argv[3]).read_text("utf-8"))["upstream"]["revisions"]
        Path(sys.argv[2]).write_text(json.dumps(fetch(pins), ensure_ascii=False), encoding="utf-8")
    else:
        pages_in = json.loads(Path(sys.argv[2]).read_text("utf-8"))
        Path(sys.argv[3]).write_text(dump(pages_in), encoding="utf-8")
        print(f"{sum(CHAPTER_VERSES)} verses")
