"""English-only supplemental sample. Not part of the population run.

Fifteen Book of Mormon verses (2013 edition) and fifteen numbered paragraphs
from the Vatican English encyclicals. Both live under
christianity/modern/english/ and are not joined into the main collect.

    python items/for-test/review/build_supplemental.py
"""

from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path

REVIEW = Path(__file__).resolve().parent
ROOT = REVIEW.parent
RAW = REVIEW.parents[2] / "texts" / "raw"
sys.path.insert(0, str(REVIEW.parents[2] / "pipelines"))

from sacredbench import catalogue as cat  # noqa: E402
from sacredbench.convert import convert_target  # noqa: E402
from sacredbench.generate import split_quote  # noqa: E402
from sacredbench.item_sample import Passage, draw_passages  # noqa: E402

MIN_WORDS = 16
N = 15
TASKS = ("retrieve_quote", "complete_unit", "cite_passage", "verify_source")
EN = {
    "retrieve_quote": "What is the text of {citation} in {version}? Reply with the exact text of that edition and nothing else.",
    "complete_unit": 'Complete this quotation from {version}: "{head}" Reply with only the remaining words.',
    "cite_passage": 'Where in {version} can I find this quote? "{text}" Answer with the citation only, in the same form as: {example}.',
    "verify_source": 'Is the following text from {version}? "{text}" Answer Yes or No.',
}


def edition_name(name: str) -> str:
    if "edition" in name.lower():
        return name
    return f"the {name} edition"


def targets(source_id: str, work: str | None = None):
    sources = cat.discover_catalogue(RAW)
    found = [t for t in cat.all_targets(sources) if t.source_id == source_id and (work is None or t.work == work)]
    if not found:
        raise SystemExit(f"no target for {source_id} {work or ''}".strip())
    return found


def book_of_mormon() -> list[tuple[Passage, str]]:
    target = targets("The Church of Jesus Christ of Latter-Day Saints", "Book of Mormon")[0]
    docs = convert_target(target.payload_paths(RAW), target)
    pool = [
        Passage(entry.citation, docs[0].work, docs[0].version)
        for entry in docs[0].entries
        if len(entry.text.split()) >= MIN_WORDS
    ]
    text = {entry.citation: entry.text for entry in docs[0].entries}
    drawn = [p for p, _ in draw_passages(pool, [], n=N, famous_share=0, seed=20261030)]
    return [(p, text[p.citation]) for p in drawn]


def encyclicals() -> list[tuple[Passage, str]]:
    target = targets("Roman Catholic", "Papal Encyclicals")[0]
    docs = convert_target(target.payload_paths(RAW), target)
    pool = []
    text = {}
    for doc in docs:
        for entry in doc.entries:
            if "unnumbered" in entry.citation or "(dup " in entry.citation:
                continue
            if len(entry.text.split()) < MIN_WORDS:
                continue
            pool.append(Passage(entry.citation, doc.work, doc.version))
            text[entry.citation] = entry.text
    drawn = [p for p, _ in draw_passages(pool, [], n=N, famous_share=0, seed=20261030)]
    return [(p, text[p.citation]) for p in drawn]


def rows_for(items, *, tradition, document_type):
    citations = [passage.citation for passage, _ in items]
    out = []
    for passage, text in items:
        head, rest = split_quote(text)
        example = next(c for c in citations if c != passage.citation)
        named = edition_name(passage.version)
        fields = {"citation": passage.citation, "version": named, "head": head, "text": text, "example": example}
        expected = {
            "retrieve_quote": {"text": text},
            "complete_unit": {"text": rest, "full_text": text},
            "cite_passage": {"citation": passage.citation},
            "verify_source": {
                "answer": "yes",
                "true_tradition": tradition,
                "true_version": passage.version,
                "true_citation": passage.citation,
            },
        }
        base = {
            "tradition": tradition,
            "work": passage.work,
            "language": "en",
            "document_type": document_type,
            "citation": passage.citation,
            "sample": "supplemental",
            "version": passage.version,
        }
        for task in TASKS:
            if task == "complete_unit" and not rest.strip():
                continue
            out.append({**base, "task": task, "condition": "en_ask_en_answer", "prompt": EN[task].format(**fields), "expected": expected[task]})
    return out


def flip_verify(groups: list[list[dict]]) -> None:
    pool = [row for group in groups for row in group if row["task"] == "retrieve_quote"]
    rng = random.Random(20261030)
    for rows in groups:
        verify = sorted((row for row in rows if row["task"] == "verify_source"), key=lambda row: row["citation"])
        for row in verify[: len(verify) // 2]:
            choices = [donor for donor in pool if donor["tradition"] != row["tradition"]]
            donor = rng.choice(choices)
            text = donor["expected"]["text"]
            row["expected"] = {
                "answer": "no",
                "true_tradition": donor["tradition"],
                "true_version": donor["version"],
                "true_citation": donor["citation"],
            }
            prompt = row["prompt"]
            a = prompt.find('"')
            b = prompt.find('"', a + 1)
            row["prompt"] = prompt[: a + 1] + text + prompt[b:]


def collect(row: dict) -> dict:
    expected = row["expected"]
    citation = "" if row["task"] == "verify_source" and expected.get("answer") == "no" else row["citation"]
    source = {
        "tradition": [row["tradition"]],
        "work": row["work"],
        "version": row["version"],
        "language": "en",
        "document_type": row["document_type"],
        "citation": citation,
        "requested_as": row["version"],
        "sample": "supplemental",
        "condition": "en_ask_en_answer",
    }
    ident = "|".join([row["tradition"], "supplemental", row["task"], row["citation"], row["prompt"]])
    return {
        "id": hashlib.sha256(ident.encode()).hexdigest()[:16],
        "task": row["task"],
        "prompt": row["prompt"],
        "expected": expected,
        "source": source,
    }


def write(folder: Path, rows: list[dict], *, notice: str) -> None:
    collected = [collect(row) for row in rows]
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "questions.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in collected),
        encoding="utf-8",
    )
    passages = []
    for row in collected:
        if row["task"] != "retrieve_quote":
            continue
        source = row["source"]
        passages.append({
            "tradition": source["tradition"][0],
            "citation": source["citation"],
            "sample": "supplemental",
            "version": source["version"],
            "text": {"english": row["expected"]["text"]},
        })
    payload = {
        "tradition": passages[0]["tradition"],
        "sample": "supplemental",
        "run": False,
        "notice": notice,
        "passages": passages,
    }
    (folder / "passages.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(folder.relative_to(ROOT), len(collected), "questions", len(passages), "passages")


def main() -> None:
    bom = rows_for(
        book_of_mormon(),
        tradition="The Church of Jesus Christ of Latter-Day Saints",
        document_type="scripture",
    )
    enc = rows_for(encyclicals(), tradition="Roman Catholic", document_type="encyclical")
    flip_verify([bom, enc])
    base = ROOT / "christianity" / "modern" / "english"
    write(
        base / "book-of-mormon",
        bom,
        notice="Book of Mormon, 2013 edition, English. Supplemental sample, not part of the NRSV population run.",
    )
    write(
        base / "encyclicals",
        enc,
        notice="Vatican English encyclicals. Supplemental sample, not part of the NRSV population run.",
    )


if __name__ == "__main__":
    main()
