"""FAccT card data (Spec 32, Phase 2).

Outcome fidelity (counts == scores.jsonl == summary.json), the Bible retrieve_quote edition
counterfactual (numerator/denominator/tags, complete_unit excluded, non-Bible never matched,
requested edition not tagged), fail-fast on inconsistent evidence, and the no-fabrication /
no-private-matcher regressions. The counterfactual reuses score.bounded_contains verbatim.
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path
from textwrap import dedent

import pytest

from sacredbench import facct as facct_mod
from sacredbench.facct import FacctError, build_facct, write_facct_json

REPO_ROOT = Path(__file__).resolve().parents[2]

PROV = (
    "provenance:\n"
    "  retrieved_from: example.org/repo\n"
    "  fetch_method: downloaded\n"
    '  fetch_date: "2026-01-01"\n'
)

# Three fixture Bible editions with deliberately disjoint wordings for Test 1:1, so a WEB
# answer to an ASV-requested citation is a clean other_edition match.
_KJV = {"Test 1:1": "alpha beta gamma delta", "Test 2:2": "mkjv two two unique",
        "Test 3:3": "kjv three correct text", "Test 5:5": "kjv five five words",
        "Test 6:6": "kjv six six alpha"}
_ASV = {"Test 1:1": "epsilon zeta eta theta", "Test 5:5": "asv five five words",
        "Test 6:6": "asv six six beta"}
_WEB = {"Test 1:1": "iota kappa lambda mu", "Test 5:5": "web five five words",
        "Test 6:6": "web six six gamma"}


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(text), encoding="utf-8")
    return path


def _bible_payload(verses: dict[str, str]) -> str:
    rows = []
    for cite, text in verses.items():
        book, cv = cite.rsplit(" ", 1)
        ch, vs = cv.split(":")
        rows.append({"book": book, "chapter": int(ch), "verse": int(vs), "text": text})
    return json.dumps(rows)


def _raw_tree(root: Path) -> Path:
    raw = root / "texts" / "raw"
    base = (
        "    converter: bible_flat\n"
        "    work: The Bible\n"
        "    language: en\n"
        "    document_type: scripture\n"
        "    tradition: [Protestant Christian]\n"
        "    license: public-domain\n"
        "    requested_as: [the Bible]\n"
        "    canonical_language: en\n"
    )
    _write(
        raw / "Protestant Christian" / "source.yaml",
        PROV + "targets:\n"
        "  - payload: kjv.json\n    version: KJV\n" + base
        + "  - payload: asv.json\n    version: ASV (1901)\n" + base
        + "  - payload: web.json\n    version: WEB\n" + base,
    )
    _write(raw / "Protestant Christian" / "kjv.json", _bible_payload(_KJV))
    _write(raw / "Protestant Christian" / "asv.json", _bible_payload(_ASV))
    _write(raw / "Protestant Christian" / "web.json", _bible_payload(_WEB))
    return raw


# (task, work, version, language, citation, answer, outcome)
_CELLS = [
    ("retrieve_quote", "The Bible", "ASV (1901)", "en", "Test 1:1", "the verse is iota kappa lambda mu", "incorrect"),  # -> tag WEB
    ("retrieve_quote", "The Bible", "KJV", "en", "Test 2:2", "nothing matching at all here", "incorrect"),  # no tag
    ("retrieve_quote", "The Bible", "KJV", "en", "Test 3:3", "kjv three correct text", "correct"),
    ("complete_unit", "The Bible", "ASV (1901)", "en", "Test 1:1", "iota kappa lambda mu", "incorrect"),  # excluded (complete_unit)
    ("retrieve_quote", "The Qur'an", "Uthmani", "ar", "2:255", "a wrong answer", "incorrect"),  # non-Bible, not matched
    ("retrieve_quote", "The Bible", "WEB", "en", "Test 5:5", "I cannot provide that", "refused"),
    # answer carries ONLY the REQUESTED edition's wording (KJV) -> must NOT be tagged other_edition
    ("retrieve_quote", "The Bible", "KJV", "en", "Test 6:6", "kjv six six alpha", "incorrect"),
]


def _make_run(root: Path, *, model: str = "m1") -> Path:
    run = root / "runs" / "fixture"
    answers, scores = [], []
    for i, (task, work, version, language, citation, answer, outcome) in enumerate(_CELLS):
        qid = f"{task}-{i:04d}"
        answers.append({
            "question_id": qid, "model_id": model, "task": task, "answer": answer,
            "question": {
                "id": qid, "task": task, "prompt": "p",
                "expected": {"text": "gold"},
                "source": {"tradition": ["T"], "work": work, "version": version,
                           "language": language, "document_type": "scripture", "citation": citation},
            },
        })
        scores.append({"question_id": qid, "model_id": model, "task": task,
                       "metrics": {"correct": int(outcome == "correct"), "outcome": outcome}})

    # summary.json counts derived from the cells so they agree by construction
    by_task: dict[str, dict] = {}
    for (task, *_rest), s in zip(_CELLS, scores):
        b = by_task.setdefault(task, {"correct": 0, "incorrect": 0, "refused": 0})
        b[s["metrics"]["outcome"]] += 1
    for b in by_task.values():
        answered = b["correct"] + b["incorrect"]
        n = answered + b["refused"]
        b["n"] = n
        b["accuracy"] = round(b["correct"] / answered, 4) if answered else 0.0
        b["coverage"] = round(answered / n, 4) if n else 0.0
    tot = {"correct": sum(b["correct"] for b in by_task.values()),
           "incorrect": sum(b["incorrect"] for b in by_task.values()),
           "refused": sum(b["refused"] for b in by_task.values())}
    answered = tot["correct"] + tot["incorrect"]
    tot["n"] = answered + tot["refused"]
    tot["accuracy"] = round(tot["correct"] / answered, 4) if answered else 0.0
    tot["coverage"] = round(answered / tot["n"], 4) if tot["n"] else 0.0
    summary = {
        "models": {model: {**by_task, "_overall": tot}},
        "panel": {model: {"provider": "p", "model": "m", "tools": []}},
        "evaluators": ["strict", "containment"],
    }
    manifest = {
        "question_set_digest": "deadbeef",
        "corpus_hash": "cafef00d",
        "n_questions": len(_CELLS),
        "selected_texts": [
            {"work": "The Bible", "version": "KJV", "language": "en"},
            {"work": "The Bible", "version": "ASV (1901)", "language": "en"},
            {"work": "The Bible", "version": "WEB", "language": "en"},
        ],
        "excluded_texts": [
            {"work": "Papal Encyclicals", "version": "Vatican English", "language": "en",
             "reason": "language 'en' != canonical_language 'la'"},
        ],
    }
    _write(run / "answers.jsonl", "\n".join(json.dumps(r) for r in answers) + "\n")
    _write(run / "scores.jsonl", "\n".join(json.dumps(r) for r in scores) + "\n")
    _write(run / "summary.json", json.dumps(summary))
    _write(run / "questions.jsonl.manifest.json", json.dumps(manifest))
    return run


def _build(tmp_path):
    raw = _raw_tree(tmp_path)
    run = _make_run(tmp_path)
    return build_facct(run, raw_root=raw), run, raw


# --- census ------------------------------------------------------------------


def test_census(tmp_path):
    report, _run, _raw = _build(tmp_path)
    c = report["census"]
    assert c["n_texts"] == 3 and c["n_questions"] == 7
    assert c["by_tradition"] == {"Protestant Christian": 3}
    assert c["by_language"] == {"en": 3}
    assert c["by_license"] == {"public-domain": 3}
    assert c["by_document_type"] == {"scripture": 3}
    assert c["excluded_texts"] == [
        {"work": "Papal Encyclicals", "version": "Vatican English", "language": "en",
         "reason": "language 'en' != canonical_language 'la'"}
    ]
    assert {t["version"] for t in c["selected_texts"]} == {"KJV", "ASV (1901)", "WEB"}


# --- outcomes ----------------------------------------------------------------


def test_outcome_counts_match_scores(tmp_path):
    report, _run, _raw = _build(tmp_path)
    rq = report["outcomes"]["m1"]["by_task"]["retrieve_quote"]
    assert (rq["correct"], rq["incorrect"], rq["refused"]) == (1, 4, 1)
    cu = report["outcomes"]["m1"]["by_task"]["complete_unit"]
    assert (cu["correct"], cu["incorrect"], cu["refused"]) == (0, 1, 0)
    ov = report["outcomes"]["m1"]["overall"]
    assert (ov["correct"], ov["incorrect"], ov["refused"]) == (1, 5, 1)
    assert ov["n"] == 7


# --- edition counterfactual --------------------------------------------------


def test_counterfactual(tmp_path):
    report, _run, _raw = _build(tmp_path)
    block = report["edition_counterfactual"]["by_model"]["m1"]
    # denominator = incorrect Bible retrieve_quote = Test 1:1 (ASV) + Test 2:2 (KJV) + Test 6:6 (KJV) = 3
    #   (the Qur'an cell is non-Bible; complete_unit is excluded; Test 3:3 correct; Test 5:5 refused)
    assert block["denominator"] == 3
    assert block["numerator"] == 1
    assert len(block["tagged"]) == 1
    tag = block["tagged"][0]
    assert tag["tag"] == "other_edition"
    assert tag["citation"] == "Test 1:1"
    assert tag["requested_version"] == "ASV (1901)"
    assert tag["other_editions"] == ["WEB"]  # requested ASV excluded; KJV wording not in the answer


def test_requested_edition_only_answer_not_tagged(tmp_path):
    report, _run, _raw = _build(tmp_path)
    block = report["edition_counterfactual"]["by_model"]["m1"]
    # the Test 6:6 cell (KJV requested, answer is exactly the KJV wording) is an incorrect Bible
    # retrieve_quote cell -> it IS in the denominator, but the requested edition is never counted
    # as "another edition", so it is NOT tagged. (Deleting the version==requested guard breaks this.)
    assert "Test 6:6" not in {t["citation"] for t in block["tagged"]}
    assert block["denominator"] == 3 and block["numerator"] == 1


def test_complete_unit_and_non_bible_excluded(tmp_path):
    report, _run, _raw = _build(tmp_path)
    tagged = report["edition_counterfactual"]["by_model"]["m1"]["tagged"]
    # the complete_unit cell (also Test 1:1 / ASV, WEB wording in its answer) is never tagged
    assert all(t["citation"] != "Test 1:1" or t["requested_version"] == "ASV (1901)" for t in tagged)
    assert len(tagged) == 1  # only the retrieve_quote one
    # and the Qur'an 2:255 cell contributes nothing (non-Bible)
    assert report["edition_counterfactual"]["by_model"]["m1"]["denominator"] == 3


def test_scope_note_mentions_bible_retrieve_quote_only(tmp_path):
    report, _run, _raw = _build(tmp_path)
    scope = report["edition_counterfactual"]["scope"].lower()
    assert "retrieve_quote" in scope and "complete_unit" in scope


# --- fail-fast ---------------------------------------------------------------


def test_missing_file_fails_fast(tmp_path):
    raw = _raw_tree(tmp_path)
    run = _make_run(tmp_path)
    (run / "summary.json").unlink()
    with pytest.raises(FacctError, match="missing required file"):
        build_facct(run, raw_root=raw)


def test_non_joining_score_row_fails_fast(tmp_path):
    raw = _raw_tree(tmp_path)
    run = _make_run(tmp_path)
    with (run / "scores.jsonl").open("a") as f:
        f.write(json.dumps({"question_id": "ghost", "model_id": "m1", "task": "retrieve_quote",
                            "metrics": {"outcome": "correct"}}) + "\n")
    with pytest.raises(FacctError, match="without an answer"):
        build_facct(run, raw_root=raw)


def test_scores_summary_disagreement_fails_fast(tmp_path):
    raw = _raw_tree(tmp_path)
    run = _make_run(tmp_path)
    summary = json.loads((run / "summary.json").read_text())
    summary["models"]["m1"]["retrieve_quote"]["incorrect"] += 5  # deliberate mismatch
    (run / "summary.json").write_text(json.dumps(summary))
    with pytest.raises(FacctError, match="disagree"):
        build_facct(run, raw_root=raw)


def test_empty_scores_fails_fast(tmp_path):
    # scores AND answers emptied (so the join is vacuously one-to-one) but summary still full:
    # the bidirectional summary check must still refuse a card with no score rows behind it.
    raw = _raw_tree(tmp_path)
    run = _make_run(tmp_path)
    (run / "scores.jsonl").write_text("")
    (run / "answers.jsonl").write_text("")
    with pytest.raises(FacctError, match="different model/task sets"):
        build_facct(run, raw_root=raw)


def test_dropped_task_scores_fails_fast(tmp_path):
    # drop complete_unit from BOTH scores and answers (join stays one-to-one); summary still lists
    # it -> the summary-set check catches a task the card would otherwise silently omit.
    raw = _raw_tree(tmp_path)
    run = _make_run(tmp_path)
    for name in ("scores.jsonl", "answers.jsonl"):
        kept = [l for l in (run / name).read_text().splitlines()
                if json.loads(l)["task"] != "complete_unit"]
        (run / name).write_text("\n".join(kept) + "\n")
    with pytest.raises(FacctError, match="different model/task sets"):
        build_facct(run, raw_root=raw)


def test_corrupted_overall_fails_fast(tmp_path):
    raw = _raw_tree(tmp_path)
    run = _make_run(tmp_path)
    summary = json.loads((run / "summary.json").read_text())
    summary["models"]["m1"]["_overall"]["correct"] += 9  # overall inconsistent with task scores
    (run / "summary.json").write_text(json.dumps(summary))
    with pytest.raises(FacctError, match="_overall"):
        build_facct(run, raw_root=raw)


def test_duplicate_answer_row_fails_fast(tmp_path):
    raw = _raw_tree(tmp_path)
    run = _make_run(tmp_path)
    first = (run / "answers.jsonl").read_text().splitlines()[0]
    with (run / "answers.jsonl").open("a") as f:
        f.write(first + "\n")  # duplicate (question_id, model_id)
    with pytest.raises(FacctError, match="duplicate answer row"):
        build_facct(run, raw_root=raw)


def test_unmatched_answer_row_fails_fast(tmp_path):
    raw = _raw_tree(tmp_path)
    run = _make_run(tmp_path)
    with (run / "answers.jsonl").open("a") as f:
        f.write(json.dumps({"question_id": "orphan", "model_id": "m1", "task": "retrieve_quote",
                            "answer": "x", "question": {"source": {}}}) + "\n")
    with pytest.raises(FacctError, match="without a score"):
        build_facct(run, raw_root=raw)


def test_score_row_missing_task_fails_fast(tmp_path):
    raw = _raw_tree(tmp_path)
    run = _make_run(tmp_path)
    # add matching answer + a score row with no 'task'
    with (run / "answers.jsonl").open("a") as f:
        f.write(json.dumps({"question_id": "notask", "model_id": "m1", "task": "retrieve_quote",
                            "answer": "x", "question": {"source": {}}}) + "\n")
    with (run / "scores.jsonl").open("a") as f:
        f.write(json.dumps({"question_id": "notask", "model_id": "m1", "metrics": {"outcome": "correct"}}) + "\n")
    with pytest.raises(FacctError, match="missing 'task'"):
        build_facct(run, raw_root=raw)


def test_build_does_not_mutate_evidence(tmp_path):
    import hashlib

    raw = _raw_tree(tmp_path)
    run = _make_run(tmp_path)
    inputs = ["scores.jsonl", "answers.jsonl", "summary.json", "questions.jsonl.manifest.json"]
    before = {f: hashlib.sha256((run / f).read_bytes()).hexdigest() for f in inputs}
    report = build_facct(run, raw_root=raw)
    write_facct_json(report, run / "facct.json")
    after = {f: hashlib.sha256((run / f).read_bytes()).hexdigest() for f in inputs}
    assert before == after  # the card never rewrites the run evidence it reads


def test_unresolved_catalogue_target_fails_fast(tmp_path):
    raw = _raw_tree(tmp_path)
    run = _make_run(tmp_path)
    manifest = json.loads((run / "questions.jsonl.manifest.json").read_text())
    manifest["selected_texts"].append({"work": "Nonexistent", "version": "X", "language": "en"})
    (run / "questions.jsonl.manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(FacctError, match="no catalogue target"):
        build_facct(run, raw_root=raw)


# --- regressions: no fabrication, no private matcher -------------------------


def test_no_fabrication_label_in_output(tmp_path):
    report, run, _raw = _build(tmp_path)
    write_facct_json(report, run / "facct.json")
    assert "fabrication" not in (run / "facct.json").read_text().lower()


def test_module_defines_no_private_containment_or_normalizer():
    src = inspect.getsource(facct_mod)
    # facct.py must reuse score's predicate, not define its own containment/normalization
    assert "score.bounded_contains" in src
    assert "def normalize" not in src
    assert "def bounded_contains" not in src  # does not redefine it


# --- real committed run ------------------------------------------------------


def test_real_run_census_and_counterfactual():
    run = REPO_ROOT / "runs" / "original-2026-10-21"
    if not run.exists() or not (REPO_ROOT / "texts" / "raw").exists():
        pytest.skip("no committed run / raw tree")
    report = build_facct(run)
    assert report["census"]["n_texts"] == 17
    assert report["census"]["zero_question_languages"] == ["grc"]
    assert {e["work"] for e in report["census"]["excluded_texts"]} == {"Papal Encyclicals", "Talmud Bavli"}
    # 32 incorrect Bible retrieve_quote cells across the panel (verified count)
    cf = report["edition_counterfactual"]["by_model"]
    assert sum(b["denominator"] for b in cf.values()) == 32
