"""FAccT benchmark-card data (Spec 32). Reworked from PR #30 (Jonathan Karr).

Reads a finished run — ``scores.jsonl``, ``summary.json``, ``answers.jsonl`` and the question
``manifest`` — plus the catalogue, and assembles the card's machine-readable data:

1. the **run census** — who the questions represent, by tradition / language / document type /
   license, the catalogue source languages that contribute zero questions, and the texts excluded
   from the pool with the manifest's reason;
2. the three **outcomes** (``correct`` / ``incorrect`` / ``refused``) taken verbatim from the
   scoring contract (``metrics.outcome`` in ``scores.jsonl``); and
3. the Bible ``retrieve_quote`` **edition counterfactual** — incorrect cells whose answer contains
   some *other* indexed edition's wording of the same citation.

It never re-scores, never calls a model, and **fails fast** (``FacctError``, no partial data) on
inconsistent evidence. Outcomes come only from ``metrics.outcome`` (``outcomes.py`` is the single
refusal definition): there is no second refusal rule and no ``fabrication`` label here. The
counterfactual reuses ``score.bounded_contains`` + ``score.normalize`` — the exact containment
predicate behind the headline — never a private matcher.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from sacredbench import catalogue as cat
from sacredbench import score
from sacredbench.edition_index import cite_key, index_documents, load_edition_documents

_BIBLE = "The Bible"
_OUTCOMES = ("correct", "incorrect", "refused")
# scope note surfaced on the card so a reader knows what the counterfactual did and did not cover
_COUNTERFACTUAL_SCOPE = (
    "Bible retrieve_quote cells only. complete_unit is excluded (its gold is a partial unit with no "
    "well-defined sibling-edition segment); the three English Bibles are the only sibling editions in "
    "the pool, and non-Bible citations (Arabic surah:ayah, hadith numbers, Talmud daf:line) are never "
    "matched to a Bible edition."
)


class FacctError(Exception):
    pass


def _load_json(path: Path) -> dict:
    if not path.exists():
        raise FacctError(f"missing required file: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise FacctError(f"{path}: not readable JSON ({e})") from e


def _load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        raise FacctError(f"missing required file: {path}")
    rows: list[dict] = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except ValueError as e:
            raise FacctError(f"{path}: line {i + 1} is not valid JSON ({e})") from e
    return rows


def _census(manifest: dict, raw_root: Path) -> dict:
    selected = manifest.get("selected_texts") or []
    excluded = manifest.get("excluded_texts") or []
    targets_by_key = {t.text_key: t for t in cat.all_targets(cat.discover_catalogue(raw_root))}

    texts: list[dict] = []
    by_tradition: Counter = Counter()
    by_language: Counter = Counter()
    by_document_type: Counter = Counter()
    by_license: Counter = Counter()
    for st in selected:
        key = (st.get("work"), st.get("version"), st.get("language"))
        target = targets_by_key.get(key)
        if target is None:
            raise FacctError(f"selected text {key} has no catalogue target")
        tradition = list(target.tradition)
        texts.append(
            {
                "work": target.work,
                "version": target.version,
                "language": target.language,
                "tradition": tradition,
                "document_type": target.document_type,
                "license": target.license,
            }
        )
        for trad in tradition:
            by_tradition[trad] += 1
        by_language[target.language] += 1
        by_document_type[target.document_type] += 1
        by_license[target.license] += 1

    # Source languages present in the catalogue that contribute zero questions to the pool.
    all_languages = {t.language for t in targets_by_key.values()}
    pool_languages = {st.get("language") for st in selected}
    zero_question_languages = sorted(all_languages - pool_languages)

    return {
        "n_texts": len(texts),
        "n_questions": manifest.get("n_questions"),
        "selected_texts": texts,
        "by_tradition": dict(sorted(by_tradition.items())),
        "by_language": dict(sorted(by_language.items())),
        "by_document_type": dict(sorted(by_document_type.items())),
        "by_license": dict(sorted(by_license.items())),
        "excluded_texts": [
            {
                "work": e.get("work"),
                "version": e.get("version"),
                "language": e.get("language"),
                "reason": e.get("reason"),
            }
            for e in excluded
        ],
        "zero_question_languages": zero_question_languages,
    }


def _outcome_counts(scores: list[dict]) -> dict[tuple[str, str], Counter]:
    counts: dict[tuple[str, str], Counter] = defaultdict(Counter)
    for s in scores:
        outcome = (s.get("metrics") or {}).get("outcome")
        if outcome not in _OUTCOMES:
            raise FacctError(
                f"score row {s.get('question_id')}/{s.get('model_id')} has unknown outcome {outcome!r}"
            )
        counts[(s["model_id"], s["task"])][outcome] += 1
    return counts


def _verify_against_summary(counts: dict[tuple[str, str], Counter], summary: dict) -> None:
    models = summary.get("models") or {}
    for (model, task), c in counts.items():
        block = (models.get(model) or {}).get(task)
        if block is None:
            raise FacctError(f"summary.json has no block for model {model!r} task {task!r}")
        for outcome in _OUTCOMES:
            if int(block.get(outcome, 0)) != c[outcome]:
                raise FacctError(
                    f"scores.jsonl and summary.json disagree for {model}/{task} on {outcome}: "
                    f"scores={c[outcome]} summary={block.get(outcome)}"
                )


def _outcomes(counts: dict[tuple[str, str], Counter], summary: dict) -> dict:
    models = summary.get("models") or {}
    out: dict[str, dict] = {}
    for model in sorted(models):
        tasks = sorted(t for (m, t) in counts if m == model)
        by_task: dict[str, dict] = {}
        for task in tasks:
            c = counts[(model, task)]
            block = models[model][task]
            by_task[task] = {
                "correct": c["correct"],
                "incorrect": c["incorrect"],
                "refused": c["refused"],
                "n": c["correct"] + c["incorrect"] + c["refused"],
                "accuracy": block.get("accuracy"),
                "coverage": block.get("coverage"),
            }
        overall = models[model].get("_overall") or {}
        out[model] = {
            "by_task": by_task,
            "overall": {
                "correct": overall.get("correct"),
                "incorrect": overall.get("incorrect"),
                "refused": overall.get("refused"),
                "accuracy": overall.get("accuracy"),
                "coverage": overall.get("coverage"),
            },
        }
    return out


def _counterfactual(scores: list[dict], ans_by: dict[tuple[str, str], dict], raw_root: Path) -> dict:
    docs, _excluded = load_edition_documents(raw_root)
    index = index_documents(docs)
    per_model: dict[str, dict] = defaultdict(lambda: {"numerator": 0, "denominator": 0, "tagged": []})
    for model_id in {s.get("model_id") for s in scores}:
        per_model[model_id]  # seed every panel model, so a model with zero misses shows 0/0

    for s in scores:
        if s.get("task") != "retrieve_quote":
            continue
        if (s.get("metrics") or {}).get("outcome") != "incorrect":
            continue
        answer_row = ans_by[(s["question_id"], s["model_id"])]
        source = (answer_row.get("question") or {}).get("source") or {}
        if source.get("work") != _BIBLE:
            continue
        model = s["model_id"]
        per_model[model]["denominator"] += 1
        citation = source.get("citation") or ""
        requested_version = source.get("version")
        key = cite_key(citation)
        if key is None:
            continue  # non-Bible-style citation: never matched to a Bible edition
        answer_text = answer_row.get("answer") or ""
        matched: list[str] = []
        for passage in index.by_cite.get(key, []):
            if passage.work != _BIBLE:  # by_cite is work-blind; Bible-only here (see EditionIndex note)
                continue
            if passage.version == requested_version:  # the requested edition is not "another edition"
                continue
            if not passage.norm or passage.version in matched:
                continue
            if score.bounded_contains(answer_text, passage.text):
                matched.append(passage.version)
        if matched:
            per_model[model]["numerator"] += 1
            per_model[model]["tagged"].append(
                {
                    "question_id": s["question_id"],
                    "citation": citation,
                    "requested_version": requested_version,
                    "other_editions": sorted(matched),
                }
            )

    for block in per_model.values():
        block["tagged"].sort(key=lambda t: (t["citation"], t["question_id"]))
    return {
        "scope": _COUNTERFACTUAL_SCOPE,
        "by_model": {m: per_model[m] for m in sorted(per_model)},
    }


def build_facct(run_dir: Path, raw_root: Path = cat.RAW_ROOT) -> dict:
    """Assemble the FAccT card data for a finished run. Pure: no model call, no re-score, no write.

    Raises :class:`FacctError` (before any caller writes anything) on missing files, a score row
    that will not join to an answer row, an unresolved catalogue target, an unknown outcome, or a
    ``scores.jsonl`` ↔ ``summary.json`` count disagreement.
    """
    run_dir = Path(run_dir)
    scores = _load_jsonl(run_dir / "scores.jsonl")
    answers = _load_jsonl(run_dir / "answers.jsonl")
    summary = _load_json(run_dir / "summary.json")
    manifest = _load_json(run_dir / "questions.jsonl.manifest.json")

    ans_by = {(a.get("question_id"), a.get("model_id")): a for a in answers}
    for s in scores:
        if (s.get("question_id"), s.get("model_id")) not in ans_by:
            raise FacctError(
                f"score row {s.get('question_id')}/{s.get('model_id')} has no matching answer row"
            )

    counts = _outcome_counts(scores)
    _verify_against_summary(counts, summary)

    return {
        "run": run_dir.name,
        "question_set_digest": manifest.get("question_set_digest"),
        "corpus_hash": manifest.get("corpus_hash"),
        "panel": summary.get("panel", {}),
        "evaluators": summary.get("evaluators", []),
        "census": _census(manifest, raw_root),
        "outcomes": _outcomes(counts, summary),
        "edition_counterfactual": _counterfactual(scores, ans_by, raw_root),
    }


def write_facct_json(report: dict, out_path: Path) -> None:
    """Write the card data to ``out_path`` (the build already validated everything)."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
