"""Map the Christian population 30 onto their original languages.

The NRSV file stays the English edition. This does not draw a second 30.
A Hebrew-Bible verse is the Masoretic text (Westminster Leningrad Codex,
Open Scriptures Hebrew Bible). A New Testament verse is the Greek New
Testament, Scrivener 1894. Daniel 2 is Aramaic inside that Masoretic text.
Each of those passages is asked twice, an English prompt and a prompt in
that verse's language, the same split as the other native editions.

    python items/for-test/review/build_christian_original.py
"""

from __future__ import annotations

import hashlib
import json
import random
import re
import urllib.request
from pathlib import Path

from sacredbench.generate import split_quote

ROOT = Path(__file__).resolve().parents[1]
OSIS = {
    "Exodus": "Exod", "Ezekiel": "Ezek", "Leviticus": "Lev", "1 Samuel": "1Sam",
    "2 Chronicles": "2Chr", "1 Kings": "1Kgs", "Judges": "Judg", "Daniel": "Dan",
    "2 Samuel": "2Sam", "1 Chronicles": "1Chr", "Isaiah": "Isa", "Jeremiah": "Jer",
    "Joshua": "Josh", "Nehemiah": "Neh",
}
NT = {"Acts", "John", "Luke", "Galatians", "Revelation", "Mark", "Hebrews", "2 Thessalonians"}
TASKS = ("retrieve_quote", "complete_unit", "cite_passage", "verify_source")
EN = {
    "retrieve_quote": "What is the text of {citation} in {version}? Reply with the exact text of that edition and nothing else.",
    "complete_unit": 'Complete this quotation from {version}: "{head}" Reply with only the remaining words.',
    "cite_passage": 'Where in {version} can I find this quote? "{text}" Answer with the citation only, in the same form as: {example}.',
    "verify_source": 'Is the following text from {version}? "{text}" Answer Yes or No.',
}
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


def split_cite(citation: str) -> tuple[str, int, int]:
    book, cv = citation.rsplit(" ", 1)
    chapter, verse = cv.split(":")
    return book, int(chapter), int(verse)


def wlc_books(citations: list[str]) -> dict[str, str]:
    books = sorted({OSIS[split_cite(c)[0]] for c in citations if split_cite(c)[0] not in NT})
    out = {}
    for book in books:
        url = f"https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/{book}.xml"
        xml = urllib.request.urlopen(url, timeout=60).read().decode("utf-8")
        for match in re.finditer(r'<verse osisID="([^"]+)">(.*?)</verse>', xml, re.S):
            text = re.sub(r"<[^>]+>", "", match.group(2))
            out[match.group(1)] = re.sub(r"\s+", " ", text).strip()
    return out


def greek_index() -> dict[tuple[str, int, int], str]:
    url = "https://raw.githubusercontent.com/honza/textus-receptus/master/data/gnt.flat.json"
    rows = json.loads(urllib.request.urlopen(url, timeout=120).read().decode("utf-8"))
    return {(row["book_name"], row["chapter"], row["verse"]): row["greek_text"].strip() for row in rows}


def donors() -> list[dict]:
    rows = []
    for path in sorted(ROOT.glob("*/*/*/prompt-native/questions.jsonl")):
        if "christianity" in path.parts:
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row["task"] == "retrieve_quote" and row["source"].get("citation"):
                rows.append(row)
    return rows


def write_group(folder: Path, rows_src: list[dict], native_tmpl: dict[str, str], notice: str) -> None:
    citations = [row["citation"] for row in rows_src]
    built = []
    for row in rows_src:
        head, rest = split_quote(row["text"])
        example = next(c for c in citations if c != row["citation"])
        fields = {"citation": row["citation"], "version": row["version"], "head": head, "text": row["text"], "example": example}
        for task in TASKS:
            expected = {
                "retrieve_quote": {"text": row["text"]},
                "complete_unit": {"text": rest, "full_text": row["text"]},
                "cite_passage": {"citation": row["citation"]},
                "verify_source": {
                    "answer": "yes", "true_tradition": "Christianity",
                    "true_version": row["version"], "true_citation": row["citation"],
                },
            }[task]
            en = EN[task].format(**fields)
            nat = native_tmpl[task].format(**fields)
            for condition, prompt in (
                ("ask_english", f"{en}\nAnswer in the language of {row['version']}."),
                ("ask_native", nat),
            ):
                built.append({
                    "task": task, "condition": condition, "prompt": prompt, "expected": expected,
                    "citation": row["citation"], "version": row["version"], "language": row["language"],
                })
    rng = random.Random(20261030)
    pool = donors()
    for condition in ("ask_english", "ask_native"):
        group = sorted((r for r in built if r["task"] == "verify_source" and r["condition"] == condition), key=lambda r: r["citation"])
        for row in group[: len(group) // 2]:
            donor = rng.choice(pool)
            foreign = donor["expected"]["text"]
            src = donor["source"]
            row["expected"] = {
                "answer": "no",
                "true_tradition": src["tradition"][0],
                "true_version": src["version"],
                "true_citation": src["citation"],
            }
            # Keep the question's citation in the id. The scored quote is the other tradition.
            if condition == "ask_english":
                row["prompt"] = EN["verify_source"].format(citation=row["citation"], version=row["version"], text=foreign, head="", example="")
                row["prompt"] += f"\nAnswer in the language of {row['version']}."
            else:
                row["prompt"] = native_tmpl["verify_source"].format(citation=row["citation"], version=row["version"], text=foreign, head="", example="")
            row["source_citation_blank"] = True
    by_prompt: dict[str, list[dict]] = {"ask_english": [], "ask_native": []}
    for row in built:
        blank = row.pop("source_citation_blank", False)
        ident = "|".join(["Christianity", "population", row["condition"], row["task"], row["citation"], row["prompt"]])
        item = {
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
                "sample": "population",
                "condition": row["condition"],
            },
        }
        by_prompt[row["condition"]].append(item)
    for condition, items in by_prompt.items():
        name = "prompt-english" if condition == "ask_english" else "prompt-native"
        path = folder / name / "questions.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in items), encoding="utf-8")
        print(path.relative_to(ROOT), len(items))
    passages = []
    for row in rows_src:
        kind = "native"
        passages.append({
            "tradition": "Christianity",
            "citation": row["citation"],
            "sample": "population",
            "version": row["version"],
            "text": {kind: row["text"]},
        })
    payload = {
        "tradition": "Christianity",
        "sample": "population",
        "run": True,
        "notice": notice,
        "passages": passages,
    }
    dest = folder / "passages.json"
    dest.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(dest.relative_to(ROOT), len(passages))


def main() -> None:
    nrsv = json.loads((ROOT / "christianity/english/population/passages.json").read_text(encoding="utf-8"))
    citations = [p["citation"] for p in nrsv["passages"]]
    if len(citations) != 30:
        raise SystemExit(f"expected 30 NRSV population passages, found {len(citations)}")
    hebrew = wlc_books(citations)
    greek = greek_index()
    masoretic, nt = [], []
    for citation in citations:
        book, chapter, verse = split_cite(citation)
        if book in NT:
            text = greek.get((book, chapter, verse))
            if not text:
                raise SystemExit(f"missing Greek verse {citation}")
            nt.append({
                "citation": citation, "text": text, "language": "grc",
                "version": "the Greek New Testament (Scrivener 1894)",
            })
        else:
            text = hebrew.get(f"{OSIS[book]}.{chapter}.{verse}")
            if not text:
                raise SystemExit(f"missing Masoretic verse {citation}")
            masoretic.append({
                "citation": citation, "text": text,
                "language": "arc" if book == "Daniel" else "he",
                "version": "the Masoretic Text (Westminster Leningrad Codex)",
            })
    if len(masoretic) + len(nt) != 30:
        raise SystemExit("the original-language map is not the same 30 passages")
    write_group(
        ROOT / "christianity" / "native" / "masoretic" / "population", masoretic, HE,
        "Masoretic text from the Westminster Leningrad Codex, via the Open Scriptures Hebrew Bible. The same 30 Christian population citations that are Hebrew Bible verses, not a second draw. Daniel 2 is Aramaic in this text.",
    )
    write_group(
        ROOT / "christianity" / "native" / "greek" / "population", nt, GR,
        "Greek New Testament, Scrivener 1894 Textus Receptus. The same 30 Christian population citations that are New Testament verses, not a second draw. Public-domain text.",
    )


if __name__ == "__main__":
    main()
