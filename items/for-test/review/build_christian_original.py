"""The Christian population 30, and the familiarity 4, in their original languages.

The NRSV file stays the English edition. This does not draw a second 30.
A Hebrew-Bible verse is the Masoretic text (Westminster Leningrad Codex,
Open Scriptures Hebrew Bible). A New Testament verse is the Greek New
Testament, Scrivener 1894. Daniel 2 is Aramaic inside that Masoretic text.
Each of those passages is asked twice, an English prompt and a prompt in
that verse's language, the same split as the other native editions.

Built by ``build_questions.py``, which draws every set's verify "no" rows from one pool.
Both texts are fetched at a pinned commit, recorded as each passages.json's provenance.
"""

from __future__ import annotations

import hashlib
import json
import re
import urllib.request
from pathlib import Path

from build_questions import EN, jsonl, passages_json, prompt_for
from sacredbench.generate import split_quote

ROOT = Path(__file__).resolve().parents[1]
WLC_URL = "https://raw.githubusercontent.com/openscriptures/morphhb/3d15126fb1ef74867fc1434be1942e837932691f/wlc/{book}.xml"
GNT_URL = "https://raw.githubusercontent.com/honza/textus-receptus/2bac2dae4a0961c84d6d544a40cbef8b8d8c4e32/data/gnt.flat.json"
MASORETIC = "the Masoretic Text (Westminster Leningrad Codex)"
GREEK = "the Greek New Testament (Scrivener 1894)"
OSIS = {
    "Exodus": "Exod", "Ezekiel": "Ezek", "Leviticus": "Lev", "1 Samuel": "1Sam",
    "2 Chronicles": "2Chr", "1 Kings": "1Kgs", "Judges": "Judg", "Daniel": "Dan",
    "2 Samuel": "2Sam", "1 Chronicles": "1Chr", "Isaiah": "Isa", "Jeremiah": "Jer",
    "Joshua": "Josh", "Nehemiah": "Neh", "Genesis": "Gen", "Psalms": "Ps",
}
NT = {"Acts", "John", "Luke", "Galatians", "Revelation", "Mark", "Hebrews", "2 Thessalonians", "Matthew"}
TASKS = ("retrieve_quote", "complete_unit", "cite_passage", "verify_source")
HE = {
    "retrieve_quote": "מהו נוסח {citation} במסורה, קודקס לנינגרד? ענה בנוסח המסורה בלבד.",
    "complete_unit": 'השלם ציטוט זה מהמסורה, קודקס לנינגרד: "{head}" ענה במילים הנותרות בלבד.',
    "cite_passage": 'היכן במסורה, קודקס לנינגרד, נמצא הטקסט הזה? "{text}" ענה בציון המקום בלבד, בצורה: {example}.',
    "verify_source": 'האם הטקסט הבא מן המסורה, קודקס לנינגרד? "{text}" ענה כן או לא.',
}
GR = {
    "retrieve_quote": "Ποιο είναι το κείμενο του {citation} στην Ελληνική Καινή Διαθήκη (Scrivener 1894); Απάντησε μόνο με το κείμενο αυτής της έκδοσης.",
    "complete_unit": 'Συμπλήρωσε αυτό το απόσπασμα από την Ελληνική Καινή Διαθήκη (Scrivener 1894): "{head}" Απάντησε μόνο με τις υπόλοιπες λέξεις.',
    "cite_passage": 'Πού στην Ελληνική Καινή Διαθήκη (Scrivener 1894) βρίσκεται αυτό το κείμενο; "{text}" Απάντησε μόνο με την παραπομπή, με τη μορφή: {example}.',
    "verify_source": 'Είναι το παρακάτω κείμενο από την Ελληνική Καινή Διαθήκη (Scrivener 1894); "{text}" Απάντησε ναι ή όχι.',
}


NOTICE = {
    ("masoretic", "population"): "Masoretic text from the Westminster Leningrad Codex, via the Open Scriptures Hebrew Bible. The same 30 Christian population citations that are Hebrew Bible verses, not a second draw. Daniel 2 is Aramaic in this text.",
    ("greek", "population"): "Greek New Testament, Scrivener 1894 Textus Receptus. The same 30 Christian population citations that are New Testament verses, not a second draw. Public-domain text.",
    ("masoretic", "familiarity"): "Familiarity panel, not in the population run. Masoretic text from the Westminster Leningrad Codex. Genesis 1:1 and Psalms 23:1 only.",
    ("greek", "familiarity"): "Familiarity panel, not in the population run. Greek New Testament, Scrivener 1894. John 3:16 and Matthew 6:9 only.",
}


def split_cite(citation: str) -> tuple[str, int, int]:
    book, cv = citation.rsplit(" ", 1)
    chapter, verse = cv.split(":")
    return book, int(chapter), int(verse)


def wlc_books(citations: list[str]) -> dict[str, str]:
    books = sorted({OSIS[split_cite(c)[0]] for c in citations if split_cite(c)[0] not in NT})
    out = {}
    for book in books:
        xml = urllib.request.urlopen(WLC_URL.format(book=book), timeout=60).read().decode("utf-8")
        for match in re.finditer(r'<verse osisID="([^"]+)">(.*?)</verse>', xml, re.S):
            text = re.sub(r"<[^>]+>", "", match.group(2))
            out[match.group(1)] = re.sub(r"\s+", " ", text).strip()
    return out


def greek_index() -> dict[tuple[str, int, int], str]:
    rows = json.loads(urllib.request.urlopen(GNT_URL, timeout=120).read().decode("utf-8"))
    return {(row["book_name"], row["chapter"], row["verse"]): row["greek_text"].strip() for row in rows}


def _rows(passages: list[dict], native_tmpl: dict[str, str], sample: str) -> list[dict]:
    """Both prompt languages of each passage, every row a "yes" until the shared negative draw."""
    citations = [p["citation"] for p in passages]
    out = []
    for p in passages:
        head, rest = split_quote(p["text"])
        example = next(c for c in citations if c != p["citation"])
        fields = {"citation": p["citation"], "version": p["version"], "head": head, "text": p["text"], "example": example}
        for task in TASKS:
            if task == "complete_unit" and sample != "population" and not rest.strip():
                continue
            expected = {
                "retrieve_quote": {"text": p["text"]},
                "complete_unit": {"text": rest, "full_text": p["text"]},
                "cite_passage": {"citation": p["citation"]},
                "verify_source": {
                    "answer": "yes", "true_tradition": "Christianity",
                    "true_version": p["version"], "true_citation": p["citation"],
                },
            }[task]
            prompts = (
                ("ask_english", prompt_for(EN[task], fields, f"\nAnswer in the language of {p['version']}.")),
                ("ask_native", prompt_for(native_tmpl[task], fields)),
            )
            for condition, prompt in prompts:
                out.append({
                    "tradition": "Christianity", "task": task, "condition": condition, "sample": sample,
                    **prompt, "expected": expected, "citation": p["citation"],
                    "version": p["version"], "language": p["language"],
                })
    return out


def build(nrsv_rows: list[dict]) -> dict[str, list[dict]]:
    """The NRSV citations, each sample in its order, split into Masoretic and Greek rows."""
    by_sample = {
        sample: [r["citation"] for r in nrsv_rows if r["task"] == "retrieve_quote" and r["sample"] == sample]
        for sample in ("population", "familiarity")
    }
    if len(by_sample["population"]) != 30:
        raise SystemExit(f"expected 30 NRSV population passages, found {len(by_sample['population'])}")
    every = by_sample["population"] + by_sample["familiarity"]
    hebrew, greek = wlc_books(every), greek_index()
    sets: dict[str, list[dict]] = {"christianity-masoretic": [], "christianity-greek": []}
    for sample, citations in by_sample.items():
        masoretic, nt = [], []
        for citation in citations:
            book, chapter, verse = split_cite(citation)
            if book in NT:
                text = greek.get((book, chapter, verse))
                if not text:
                    raise SystemExit(f"missing Greek verse {citation}")
                nt.append({"citation": citation, "text": text, "language": "grc", "version": GREEK})
            else:
                text = hebrew.get(f"{OSIS[book]}.{chapter}.{verse}")
                if not text:
                    raise SystemExit(f"missing Masoretic verse {citation}")
                language = "arc" if book == "Daniel" else "he"
                masoretic.append({"citation": citation, "text": text, "language": language, "version": MASORETIC})
        sets["christianity-masoretic"] += _rows(masoretic, HE, sample)
        sets["christianity-greek"] += _rows(nt, GR, sample)
    return sets


def _item(row: dict) -> dict:
    blank = row["task"] == "verify_source" and row["expected"]["answer"] == "no"
    ident = "|".join(["Christianity", row["sample"], row["condition"], row["task"], row["citation"], row["prompt"]])
    return {
        "id": hashlib.sha256(ident.encode()).hexdigest()[:16],
        "task": row["task"],
        "prompt": row["prompt"],
        "expected": row["expected"],
        "source": {
            "tradition": ["Christianity"],
            "work": "The Bible",
            "version": row["version"],
            "language": row["language"],
            "document_type": "scripture",
            "citation": "" if blank else row["citation"],
            "requested_as": row["version"],
            "sample": row["sample"],
            "condition": row["condition"],
        },
    }


def output_files(sets: dict[str, list[dict]]) -> dict[Path, str]:
    """christianity/native/{masoretic,greek}/<sample>/: both prompt languages and passages.json."""
    files = {}
    for edition, url in (("masoretic", WLC_URL), ("greek", GNT_URL)):
        for sample in ("population", "familiarity"):
            rows = [r for r in sets[f"christianity-{edition}"] if r["sample"] == sample]
            folder = ROOT / "christianity" / "native" / edition / sample
            for condition, name in (("ask_english", "prompt-english"), ("ask_native", "prompt-native")):
                files[folder / name / "questions.jsonl"] = jsonl([_item(r) for r in rows if r["condition"] == condition])
            files[folder / "passages.json"] = passages_json({
                "tradition": "Christianity", "sample": sample, "run": sample == "population",
                "passages": [
                    {"tradition": "Christianity", "citation": r["citation"], "sample": sample,
                     "version": r["version"], "text": {"native": r["expected"]["text"]}}
                    for r in rows if r["task"] == "retrieve_quote" and r["condition"] == "ask_native"
                ],
                "notice": NOTICE[(edition, sample)],
                "provenance": url,
            })
    return files
