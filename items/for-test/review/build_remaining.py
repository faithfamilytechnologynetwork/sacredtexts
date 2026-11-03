"""Population samples for the Bhagavad Gita and the Dhammapada.

Hinduism is one draw of 30. The 16-word floor is Besant's English, because only
16 Sanskrit verses reach 16 words. Those citations are asked in Sanskrit
(English prompt and Sanskrit prompt) and again in Besant's English.

Buddhism is 30 Pali verses of at least 16 words. This corpus has no English
Dhammapada, so there is no english/ folder. The Pali text is asked with the
English prompt only. Romanized Pali has no native speakers, so a Pali-language
prompt measures nothing comparable to the other native prompts (owner decision, #113).

Familiarity is every Gita and Dhammapada line in well_known.yaml, outside the population draw.

Built by ``build_questions.py``, which draws every set's verify "no" rows from one pool.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

REVIEW = Path(__file__).resolve().parent
ROOT = REVIEW.parent
RAW = REVIEW.parents[2] / "texts" / "raw"
sys.path.insert(0, str(REVIEW.parents[2] / "pipelines"))

from sacredbench import catalogue as cat  # noqa: E402
from sacredbench.convert import convert_target  # noqa: E402
from sacredbench.generate import split_quote  # noqa: E402
from sacredbench.item_sample import Passage, draw_passages, load_well_known  # noqa: E402
from build_questions import EN, edition_name, jsonl, passages_json, prompt_for, prompt_text  # noqa: E402

MIN_WORDS = 16
TASKS = ("retrieve_quote", "complete_unit", "cite_passage", "verify_source")
# The Sanskrit prompts name the work in the prompt's own language, as the Hebrew, Punjabi and
# Arabic ones do, rather than splicing in the English edition string (issue #90).
SA = {
    "retrieve_quote": "{citation} का पाठ श्रीमद्भगवद्गीता (स्तोत्र संहिता, गीता प्रेस पाठ) में क्या है? केवल उसी संस्करण का पाठ लिखें।",
    "complete_unit": 'श्रीमद्भगवद्गीता (स्तोत्र संहिता, गीता प्रेस पाठ) से यह उद्धरण पूरा करें: "{head}" केवल शेष शब्द लिखें।',
    "cite_passage": 'श्रीमद्भगवद्गीता (स्तोत्र संहिता, गीता प्रेस पाठ) में यह उद्धरण कहाँ है? "{text}" केवल संकेत लिखें, इस रूप में: {example}।',
    "verify_source": 'क्या यह पाठ श्रीमद्भगवद्गीता (स्तोत्र संहिता, गीता प्रेस पाठ) से है? "{text}" हाँ या नहीं लिखें।',
}


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


def question_rows(items, *, tradition, work, language, version, native_tmpl, document_type="scripture", sample="population"):
    """The English-prompt row of each task, then the native-prompt row unless ``native_tmpl`` is None."""
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
            "language": language,
            "document_type": document_type,
            "citation": passage.citation,
            "sample": sample,
            "version": version,
        }
        for task in TASKS:
            if task == "complete_unit" and not rest.strip():
                continue
            out.append({
                **base,
                "task": task,
                "condition": "ask_english",
                **prompt_for(EN[task], fields, f"\nAnswer in the language of {edition_name(version)}."),
                "expected": expected[task],
            })
            if native_tmpl is None:
                continue
            out.append({
                **base,
                "task": task,
                "condition": "ask_native",
                **prompt_for(native_tmpl[task], fields),
                "expected": expected[task],
            })
    return out


def english_rows(items, *, tradition, work, version, sample="population"):
    citations = [passage.citation for passage, _ in items]
    out = []
    for passage, text in items:
        head, rest = split_quote(text)
        example = next(c for c in citations if c != passage.citation)
        fields = {
            "citation": passage.citation,
            "version": edition_name(version),
            "head": prompt_text(head),
            "text": prompt_text(text),
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
            "sample": sample,
            "version": version,
        }
        for task in TASKS:
            if task == "complete_unit" and not rest.strip():
                continue
            out.append({
                **base,
                "task": task,
                "condition": "en_ask_en_answer",
                **prompt_for(EN[task], fields),
                "expected": expected[task],
            })
    return out


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


SA_VERSION = "Stotra Samhita (Gita Press text)"
EN_VERSION = "Annie Besant (1922)"
PI_VERSION = "Chaṭṭha Saṅgāyana (VRI)"
NOTICE = {
    ("hinduism", "population"): "Sanskrit is the Stotra Samhita extract of the Gita Press text. English is Annie Besant, 1922, public domain. The 30 citations are one draw; the 16-word floor is the English wording.",
    ("buddhism", "population"): "Dhammapada, Chaṭṭha Saṅgāyana edition, Vipassana Research Institute. Non-commercial use; attribute VRI. No English edition of this work is in the corpus.",
    ("hinduism", "familiarity"): "Familiarity panel, not in the population run. Sanskrit is the Stotra Samhita extract. English is Annie Besant, 1922.",
    ("buddhism", "familiarity"): "Familiarity panel, not in the population run. Dhammapada, Chaṭṭha Saṅgāyana edition, Vipassana Research Institute. No English edition of this work is in the corpus.",
}


def build() -> dict[str, list[dict]]:
    """The Gita (Sanskrit, both prompts, then Besant) and the Dhammapada (Pali, English prompt), population then familiarity.

    The pre-registered lines in well_known.yaml are not in either drawn 30.
    """
    sanskrit, besant, pali = entries("Hinduism", SA_VERSION), entries("Hinduism", EN_VERSION), entries("Buddhism", PI_VERSION)
    eligible = [
        Passage(citation, "Bhagavad Gita", EN_VERSION)
        for citation in sorted(set(sanskrit) & set(besant))
        if len(besant[citation].split()) >= MIN_WORDS
    ]
    known = load_well_known(ROOT / "well_known.yaml")
    gita = {"population": population(eligible, seed=20261030), "familiarity": [p for p in known if p.work == "Bhagavad Gita"]}
    dhp_pool = [Passage(c, "Dhammapada", PI_VERSION) for c, text in pali.items() if len(text.split()) >= MIN_WORDS]
    dhp = {"population": population(dhp_pool, seed=20261030), "familiarity": [p for p in known if p.work == "Dhammapada"]}
    sets: dict[str, list[dict]] = {"hinduism": [], "buddhism": []}
    for sample in ("population", "familiarity"):
        sets["hinduism"] += question_rows(
            [(p, sanskrit[p.citation]) for p in gita[sample]], tradition="Hinduism", work="Bhagavad Gita",
            language="sa", version=SA_VERSION, native_tmpl=SA, sample=sample,
        ) + english_rows(
            [(p, besant[p.citation]) for p in gita[sample]], tradition="Hinduism", work="Bhagavad Gita",
            version=EN_VERSION, sample=sample,
        )
        sets["buddhism"] += question_rows(
            [(p, pali[p.citation]) for p in dhp[sample]], tradition="Buddhism", work="Dhammapada",
            language="pi", version=PI_VERSION, native_tmpl=None, sample=sample,
        )
    return sets


def _passages(rows: list[dict], *, notice: str, sample: str) -> str:
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
    return passages_json({
        "tradition": passages[0]["tradition"], "sample": sample, "run": sample == "population",
        "notice": notice, "passages": passages,
    })


def output_files(sets: dict[str, list[dict]]) -> dict[Path, str]:
    """<tradition>/native/<sample>/prompt-*/ and <tradition>/english/<sample>/, each with passages.json."""
    files = {}
    for (tradition, sample), notice in NOTICE.items():
        collected = [collect(row) for row in sets[tradition] if row["sample"] == sample]
        for condition in ("ask_english", "ask_native", "en_ask_en_answer"):
            group = [row for row in collected if row["source"]["condition"] == condition]
            if not group:
                continue
            if condition == "en_ask_en_answer":
                folder = ROOT / tradition / "english" / sample
                files[folder / "passages.json"] = _passages(group, notice=notice, sample=sample)
            else:
                prompt = {"ask_english": "prompt-english", "ask_native": "prompt-native"}[condition]
                folder = ROOT / tradition / "native" / sample / prompt
                if condition == "ask_english":
                    files[folder.parent / "passages.json"] = _passages(group, notice=notice, sample=sample)
            files[folder / "questions.jsonl"] = jsonl(group)
    return files
