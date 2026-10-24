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


def _index_unique(rows: list[dict], kind: str) -> dict[tuple[str, str], dict]:
    """Index rows by ``(question_id, model_id)``, failing fast on a missing or duplicate key."""
    out: dict[tuple[str, str], dict] = {}
    for r in rows:
        key = (r.get("question_id"), r.get("model_id"))
        if key[0] is None or key[1] is None:
            raise FacctError(f"{kind} row missing question_id/model_id: {key}")
        if key in out:
            raise FacctError(f"duplicate {kind} row for {key}")
        out[key] = r
    return out


def _outcome_counts(scores: list[dict]) -> dict[tuple[str, str], Counter]:
    counts: dict[tuple[str, str], Counter] = defaultdict(Counter)
    for s in scores:
        task = s.get("task")
        if task is None:
            raise FacctError(f"score row {s.get('question_id')}/{s.get('model_id')} is missing 'task'")
        outcome = (s.get("metrics") or {}).get("outcome")
        if outcome not in _OUTCOMES:
            raise FacctError(
                f"score row {s.get('question_id')}/{s.get('model_id')} has unknown outcome {outcome!r}"
            )
        counts[(s["model_id"], task)][outcome] += 1
    return counts


def _verify_against_summary(counts: dict[tuple[str, str], Counter], summary: dict) -> None:
    """Both directions: the scores' (model, task) set must equal the summary's, every per-task
    outcome count must agree, and each model's ``_overall`` must equal the sum of its task counts —
    so neither an empty/short ``scores.jsonl`` nor a corrupted ``_overall`` can slip through."""
    models = summary.get("models") or {}
    score_keys = set(counts)
    summary_keys = {
        (model, task)
        for model, blocks in models.items()
        for task in blocks
        if task != "_overall"
    }
    if score_keys != summary_keys:
        raise FacctError(
            "scores.jsonl and summary.json cover different model/task sets: "
            f"only-in-scores={sorted(score_keys - summary_keys)}, "
            f"only-in-summary={sorted(summary_keys - score_keys)}"
        )
    for (model, task), c in counts.items():
        block = models[model][task]
        for outcome in _OUTCOMES:
            if int(block.get(outcome, 0)) != c[outcome]:
                raise FacctError(
                    f"scores.jsonl and summary.json disagree for {model}/{task} on {outcome}: "
                    f"scores={c[outcome]} summary={block.get(outcome)}"
                )
    for model in models:
        agg = Counter()
        for (m, _task), c in counts.items():
            if m == model:
                for outcome in _OUTCOMES:
                    agg[outcome] += c[outcome]
        overall = models[model].get("_overall") or {}
        for outcome in _OUTCOMES:
            if int(overall.get(outcome, 0)) != agg[outcome]:
                raise FacctError(
                    f"summary.json _overall for {model} disagrees with the summed task scores on "
                    f"{outcome}: _overall={overall.get(outcome)} scores={agg[outcome]}"
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
        # overall COUNTS are summed from the verified per-task scores (not copied from summary),
        # so the card's overall can never disagree with its own by_task; accuracy/coverage are the
        # derived rates from the (now count-verified) summary _overall.
        overall_summary = models[model].get("_overall") or {}
        agg = {o: sum(by_task[t][o] for t in by_task) for o in _OUTCOMES}
        out[model] = {
            "by_task": by_task,
            "overall": {
                **agg,
                "n": sum(agg.values()),
                "accuracy": overall_summary.get("accuracy"),
                "coverage": overall_summary.get("coverage"),
            },
        }
    return out


def _counterfactual(scores: list[dict], ans_by: dict[tuple[str, str], dict], raw_root: Path) -> dict:
    docs, _excluded = load_edition_documents(raw_root)
    index = index_documents(docs)
    per_model: dict[str, dict] = {}
    for model_id in {s.get("model_id") for s in scores}:
        per_model[model_id] = {"numerator": 0, "denominator": 0, "tagged": []}  # seed so 0-miss models show 0/0

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
                    "tag": "other_edition",
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

    ans_by = _index_unique(answers, "answer")
    score_by = _index_unique(scores, "score")
    if set(score_by) != set(ans_by):
        only_scores = sorted(set(score_by) - set(ans_by))
        only_answers = sorted(set(ans_by) - set(score_by))
        raise FacctError(
            f"scores.jsonl and answers.jsonl do not join one-to-one: "
            f"{len(only_scores)} score row(s) without an answer (e.g. {only_scores[:3]}), "
            f"{len(only_answers)} answer row(s) without a score (e.g. {only_answers[:3]})"
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
