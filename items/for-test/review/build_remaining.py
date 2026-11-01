"""Population samples for the Bhagavad Gita and the Dhammapada.

Hinduism is one draw of 30. The 16-word floor is Besant's English, because only
16 Sanskrit verses reach 16 words. Those citations are asked in Sanskrit
(English prompt and Sanskrit prompt) and again in Besant's English.

Buddhism is 30 Pali verses of at least 16 words. This corpus has no English
Dhammapada, so there is no english/ folder.

Neither work is listed in well_known.yaml, so there is no familiarity panel.

    python items/for-test/review/build_remaining.py
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
TASKS = ("retrieve_quote", "complete_unit", "cite_passage", "verify_source")
EN = {
    "retrieve_quote": "What is the text of {citation} in {version}? Reply with the exact text of that edition and nothing else.",
    "complete_unit": 'Complete this quotation from {version}: "{head}" Reply with only the remaining words.',
    "cite_passage": 'Where in {version} can I find this quote? "{text}" Answer with the citation only, in the same form as: {example}.',
    "verify_source": 'Is the following text from {version}? "{text}" Answer Yes or No.',
}
SA = {
    "retrieve_quote": "{citation} का पाठ {version} में क्या है? केवल उसी संस्करण का पाठ लिखें।",
    "complete_unit": '{version} से यह उद्धरण पूरा करें: "{head}" केवल शेष शब्द लिखें।',
    "cite_passage": '{version} में यह उद्धरण कहाँ है? "{text}" केवल संकेत लिखें, इस रूप में: {example}।',
    "verify_source": 'क्या यह पाठ {version} से है? "{text}" हाँ या नहीं लिखें।',
}
PI = {
    "retrieve_quote": "Ko {citation} pāṭho {version} potthake? Tasseva pāṭham eva vissajjehi.",
    "complete_unit": '{version} ito imaṃ udāharaṇaṃ paripūrehi: "{head}" Avasiṭṭhapadāni yeva vissajjehi.',
    "cite_passage": 'Kattha {version} potthake ayaṃ pāṭho? "{text}" Ṭhānam eva vissajjehi, iminā ākārena: {example}.',
    "verify_source": 'Ayaṃ pāṭho {version} potthakato? "{text}" Āma vā no vā vissajjehi.',
}


def edition_name(name: str) -> str:
    if "edition" in name.lower():
        return name
    return f"the {name} edition"


def entries(source_id: str, version: str) -> dict[str, str]:
    sources = cat.discover_catalogue(RAW)
    matches = [t for t in cat.all_targets(sources) if t.source_id == source_id and t.version == version]
    if len(matches) != 1:
        raise SystemExit(f"{source_id} / {version}: expected one target, found {len(matches)}")
    docs = convert_target(matches[0].payload_paths(RAW), matches[0])
    if len(docs) != 1:
        raise SystemExit(f"{version}: expected one document, found {len(docs)}")
    return {entry.citation: entry.text for entry in docs[0].entries}


def population(pool: list[Passage], *, seed: int) -> list[Passage]:
    return [p for p, _ in draw_passages(pool, [], n=30, famous_share=0, seed=seed)]


def question_rows(items, *, tradition, work, language, version, native_tmpl, document_type="scripture"):
    citations = [passage.citation for passage, _ in items]
    out = []
    for passage, text in items:
        head, rest = split_quote(text)
        example = next(c for c in citations if c != passage.citation)
        fields = {
            "citation": passage.citation,
            "version": edition_name(version),
            "head": head,
            "text": text,
            "example": example,
        }
        en_q = {task: EN[task].format(**fields) for task in TASKS}
        nat_q = {task: native_tmpl[task].format(**fields) for task in TASKS}
        expected = {
            "retrieve_quote": {"text": text},
            "complete_unit": {"text": rest, "full_text": text},
            "cite_passage": {"citation": passage.citation},
            "verify_source": {
                "answer": "yes",
                "true_tradition": tradition,
                "true_version": version,
                "true_citation": passage.citation,
            },
        }
        base = {
            "tradition": tradition,
            "work": work,
            "language": language,
            "document_type": document_type,
            "citation": passage.citation,
            "sample": "population",
            "version": version,
        }
        for task in TASKS:
            if task == "complete_unit" and not rest.strip():
                continue
            out.append({
                **base,
                "task": task,
                "condition": "ask_english",
                "prompt": f"{en_q[task]}\nAnswer in the language of {edition_name(version)}.",
                "expected": expected[task],
            })
            out.append({
                **base,
                "task": task,
                "condition": "ask_native",
                "prompt": nat_q[task],
                "expected": expected[task],
            })
    return out


def english_rows(items, *, tradition, work, version):
    citations = [passage.citation for passage, _ in items]
    out = []
    for passage, text in items:
        head, rest = split_quote(text)
        example = next(c for c in citations if c != passage.citation)
        fields = {
            "citation": passage.citation,
            "version": edition_name(version),
            "head": head,
            "text": text,
            "example": example,
        }
        expected = {
            "retrieve_quote": {"text": text},
            "complete_unit": {"text": rest, "full_text": text},
            "cite_passage": {"citation": passage.citation},
            "verify_source": {
                "answer": "yes",
                "true_tradition": tradition,
                "true_version": version,
                "true_citation": passage.citation,
            },
        }
        base = {
            "tradition": tradition,
            "work": work,
            "language": "en",
            "document_type": "scripture",
            "citation": passage.citation,
            "sample": "population",
            "version": version,
        }
        for task in TASKS:
            if task == "complete_unit" and not rest.strip():
                continue
            out.append({
                **base,
                "task": task,
                "condition": "en_ask_en_answer",
                "prompt": EN[task].format(**fields),
                "expected": expected[task],
            })
    return out


def donors() -> list[dict]:
    found = []
    for path in list(ROOT.glob("*/*/*/questions.jsonl")) + list(ROOT.glob("*/*/*/*/questions.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            source = row.get("source")
            if row["task"] != "retrieve_quote" or not source:
                continue
            found.append({
                "tradition": source["tradition"][0],
                "version": source["version"],
                "citation": source["citation"],
                "condition": source["condition"],
                "expected": row["expected"],
            })
    return found


def add_verify_negatives(groups: list[list[dict]], pool: list[dict]) -> None:
    rng = random.Random(20261030)
    for rows in groups:
        by_condition: dict[str, list[dict]] = {}
        for row in rows:
            if row["task"] == "verify_source":
                by_condition.setdefault(row["condition"], []).append(row)
        for group in by_condition.values():
            group.sort(key=lambda row: row["citation"])
            for row in group[: len(group) // 2]:
                same = [
                    donor for donor in pool
                    if donor["tradition"] != row["tradition"] and donor["condition"] == row["condition"]
                ]
                choices = same or [donor for donor in pool if donor["tradition"] != row["tradition"]]
                donor = rng.choice(choices)
                text = donor["expected"]["text"]
                row["expected"] = {
                    "answer": "no",
                    "true_tradition": donor["tradition"],
                    "true_version": donor["version"],
                    "true_citation": donor["citation"],
                }
                lines = row["prompt"].split("\n")
                for i, line in enumerate(lines):
                    a = line.find('"')
                    b = line.find('"', a + 1) if a != -1 else -1
                    if a != -1 and b != -1:
                        lines[i] = line[: a + 1] + text + line[b:]
                row["prompt"] = "\n".join(lines)


def collect(row: dict) -> dict:
    language = "en" if row["condition"] == "en_ask_en_answer" else row["language"]
    expected = row["expected"]
    citation = "" if row["task"] == "verify_source" and expected.get("answer") == "no" else row["citation"]
    source = {
        "tradition": [row["tradition"]],
        "work": row["work"],
        "version": row["version"],
        "language": language,
        "document_type": row["document_type"],
        "citation": citation,
        "requested_as": row["version"],
        "sample": row["sample"],
        "condition": row["condition"],
    }
    ident = "|".join([
        row["tradition"], row["sample"], row["condition"], row["task"], row["citation"], row["prompt"],
    ])
    return {
        "id": hashlib.sha256(ident.encode()).hexdigest()[:16],
        "task": row["task"],
        "prompt": row["prompt"],
        "expected": expected,
        "source": source,
    }


def write_questions(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    print(path.relative_to(ROOT), len(rows))


def write_passages(folder: Path, rows: list[dict], *, notice: str) -> None:
    passages = []
    for row in rows:
        if row["task"] != "retrieve_quote":
            continue
        source = row["source"]
        kind = "english" if source["language"] == "en" else "native"
        passages.append({
            "tradition": source["tradition"][0],
            "citation": source["citation"],
            "sample": source["sample"],
            "version": source["version"],
            "text": {kind: row["expected"]["text"]},
        })
    payload = {
        "tradition": passages[0]["tradition"],
        "sample": "population",
        "run": True,
        "notice": notice,
        "passages": passages,
    }
    dest = folder / "passages.json"
    dest.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(dest.relative_to(ROOT), len(passages))


def place(rows: list[dict], *, notice: str) -> list[str]:
    collected = [collect(row) for row in rows]
    by_condition: dict[str, list[dict]] = {}
    for row in collected:
        by_condition.setdefault(row["source"]["condition"], []).append(row)
    tradition = collected[0]["source"]["tradition"][0].lower()
    citations = []
    for condition, group in by_condition.items():
        if condition == "en_ask_en_answer":
            folder = ROOT / tradition / "english" / "population"
            write_questions(folder / "questions.jsonl", group)
            write_passages(folder, group, notice=notice)
        else:
            prompt = {"ask_english": "prompt-english", "ask_native": "prompt-native"}[condition]
            folder = ROOT / tradition / "native" / "population" / prompt
            write_questions(folder / "questions.jsonl", group)
            if condition == "ask_native":
                write_passages(folder.parent, group, notice=notice)
                citations = [row["source"]["citation"] for row in group if row["task"] == "retrieve_quote"]
    return citations


def review_page(*, folder, title, version, english_version, language, source, native, citations) -> None:
    lines = [
        f"# {title}",
        "",
        f"- Canonical edition named in the question: **{version}**",
        f"- English edition: **{english_version}**",
        f"- Language: {language}",
        f"- Raw file: `{source}`",
        "- Tasks: retrieve_quote, complete_unit, cite_passage, verify_source",
        f"- Size: population sample of {len(citations)} passages. No familiarity list in `well_known.yaml`.",
        "",
        "## Passages to check",
        "",
    ]
    for citation in citations:
        lines.append(f"- `{citation}` (population)")
    lines.extend([
        "",
        "These citations are the question file. Population and familiarity are separate samples.",
        "",
        "## Prompts in English",
        "",
        '- `retrieve_quote`: What is the text of {citation} in {version}? Reply with the exact text of that edition and nothing else.',
        '- `complete_unit`: Complete this quotation from {version}: "{head}" Reply with only the remaining words.',
        '- `cite_passage`: Where in {version} can I find this quote? "{text}" Answer with the citation only, in the same form as: {example}.',
        '- `verify_source`: Is the following text from {version}? "{text}" Answer Yes or No.',
        "",
        "## Prompts in the text's language (draft)",
        "",
        "A native speaker should correct these before a run.",
        "",
    ])
    for task, tmpl in native.items():
        lines.append(f"- `{task}`: {tmpl}")
    lines.append("")
    dest = REVIEW / folder / "README.md"
    dest.write_text("\n".join(lines), encoding="utf-8")
    print(dest.relative_to(ROOT))


def main() -> None:
    sanskrit = entries("Hinduism", "Stotra Samhita (Gita Press text)")
    besant = entries("Hinduism", "Annie Besant (1922)")
    shared = sorted(set(sanskrit) & set(besant))
    eligible = [
        Passage(citation, "Bhagavad Gita", "Annie Besant (1922)")
        for citation in shared
        if len(besant[citation].split()) >= MIN_WORDS
    ]
    drawn = population(eligible, seed=20261030)
    native_items = [(passage, sanskrit[passage.citation]) for passage in drawn]
    english_items = [(passage, besant[passage.citation]) for passage in drawn]
    sa_version = "Stotra Samhita (Gita Press text)"
    en_version = "Annie Besant (1922)"
    hindu_native = question_rows(
        native_items,
        tradition="Hinduism",
        work="Bhagavad Gita",
        language="sa",
        version=sa_version,
        native_tmpl=SA,
    )
    hindu_english = english_rows(
        english_items,
        tradition="Hinduism",
        work="Bhagavad Gita",
        version=en_version,
    )

    pali = entries("Buddhism", "Chaṭṭha Saṅgāyana (VRI)")
    pi_version = "Chaṭṭha Saṅgāyana (VRI)"
    buddhist_pool = [
        Passage(citation, "Dhammapada", pi_version)
        for citation, text in pali.items()
        if len(text.split()) >= MIN_WORDS
    ]
    buddhist_drawn = population(buddhist_pool, seed=20261030)
    buddhist = question_rows(
        [(passage, pali[passage.citation]) for passage in buddhist_drawn],
        tradition="Buddhism",
        work="Dhammapada",
        language="pi",
        version=pi_version,
        native_tmpl=PI,
    )

    add_verify_negatives([hindu_native, hindu_english, buddhist], donors())
    hindu_citations = place(
        hindu_native + hindu_english,
        notice="Sanskrit is the Stotra Samhita extract of the Gita Press text. English is Annie Besant, 1922, public domain. The 30 citations are one draw; the 16-word floor is the English wording.",
    )
    buddhist_citations = place(
        buddhist,
        notice="Dhammapada, Chaṭṭha Saṅgāyana edition, Vipassana Research Institute. Non-commercial use; attribute VRI. No English edition of this work is in the corpus.",
    )
    review_page(
        folder="05-hinduism",
        title="Hinduism",
        version="Bhagavad Gita, Stotra Samhita (Gita Press text)",
        english_version="Annie Besant (1922), same 30 citations",
        language="Sanskrit, then English",
        source="texts/raw/Hinduism/gita_stotrasamhita.json and gita_besant.json",
        native=SA,
        citations=hindu_citations,
    )
    review_page(
        folder="06-buddhism",
        title="Buddhism",
        version="Dhammapada, Chaṭṭha Saṅgāyana (VRI)",
        english_version="none in this corpus",
        language="Pali (romanized)",
        source="texts/raw/Buddhism/s0502m.mul.xml",
        native=PI,
        citations=buddhist_citations,
    )


if __name__ == "__main__":
    main()
