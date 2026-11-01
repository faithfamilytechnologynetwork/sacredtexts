"""Point existing verify_source "no" rows at a same-language near miss.

Keeps which rows are "no". Replaces only the quoted passage and the scorer's
true_tradition / true_version / true_citation. Question ids stay put.

A language with only one work in this corpus is left as a cross-tradition donor.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NT = {
    "Matthew", "Mark", "Luke", "John", "Acts", "Romans", "1 Corinthians", "2 Corinthians",
    "Galatians", "Ephesians", "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians",
    "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews", "James", "1 Peter", "2 Peter",
    "1 John", "2 John", "3 John", "Jude", "Revelation",
}


def family(language: str) -> str:
    if language in {"he", "arc"}:
        return "he"
    return language


def book(citation: str) -> str:
    if " " not in citation or ":" not in citation:
        return ""
    return citation.rsplit(" ", 1)[0]


def wanted(row_lang: str, row_work: str, row_version: str):
    """Return a predicate for the preferred donor, or None when no near miss exists."""
    fam = family(row_lang)
    if row_work == "Talmud Bavli" and fam == "he":
        return lambda d: d["work"] == "The Bible" and "Masoretic" in d["version"]
    if row_work == "Talmud Bavli" and fam == "en":
        return lambda d: d["work"] == "The Bible" and d["version"] == "NRSV" and book(d["citation"]) not in NT
    if row_work == "The Bible" and "Masoretic" in row_version:
        return lambda d: d["work"] == "Talmud Bavli" and family(d["language"]) == "he"
    if row_work == "The Bible" and row_version == "NRSV":
        return lambda d: d["work"] == "Book of Mormon"
    return None


def load_donors() -> list[dict]:
    seen = set()
    donors = []
    for path in ROOT.glob("*/*/**/questions.jsonl"):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row["task"] != "retrieve_quote":
                continue
            source = row["source"]
            key = (source["work"], source["version"], source["citation"])
            if key in seen:
                continue
            seen.add(key)
            donors.append({
                "work": source["work"],
                "version": source["version"],
                "language": source["language"],
                "tradition": source["tradition"][0],
                "citation": source["citation"],
                "text": row["expected"]["text"],
            })
    return donors


def splice(prompt: str, text: str) -> str:
    text = text.replace('"', "'")
    head, sep, tail = prompt.partition("\n")
    start = head.find('"')
    end = head.rfind('"')
    if start == -1 or end <= start:
        raise SystemExit(f"no quotation marks in: {prompt[:80]}")
    head = head[: start + 1] + text + head[end:]
    return head + sep + tail


def main() -> None:
    donors = load_donors()
    rng = random.Random(20261030)
    for path in sorted(ROOT.glob("*/*/**/questions.jsonl")):
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        yes = next(row for row in rows if row["task"] == "retrieve_quote")
        source = yes["source"]
        prefer = wanted(source["language"], source["work"], source["version"])
        if prefer is None:
            continue
        pool = [d for d in donors if prefer(d)]
        if not pool:
            raise SystemExit(f"no donor for {path}")
        changed = 0
        for row in rows:
            if row["task"] != "verify_source" or row["expected"].get("answer") != "no":
                continue
            donor = rng.choice(pool)
            row["prompt"] = splice(row["prompt"], donor["text"])
            row["expected"] = {
                "answer": "no",
                "true_tradition": donor["tradition"],
                "true_version": donor["version"],
                "true_citation": donor["citation"],
            }
            changed += 1
        path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
        print(path.relative_to(ROOT), changed)


if __name__ == "__main__":
    main()
