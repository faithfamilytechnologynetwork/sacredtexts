"""Spec 154 phase 1: the review sample is an even, seeded, stratified, byte-stable draw."""

from __future__ import annotations

import json
import subprocess
from collections import Counter
from pathlib import Path

import pytest

from sacredbench.review_sample import (
    ReviewSampleError,
    build_sample,
    dumps_sample,
    grader_path,
    load_sample,
    write_sample,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
COMMITTED = REPO_ROOT / "review" / "samples" / "facct-2026-11-03-k10.json"
COMMITTED_SEED = "spec-154"
COMMITTED_K = 10


def _source(work: str, version: str, language: str) -> dict:
    return {"work": work, "version": version, "language": language, "tradition": ["T"], "citation": "1:1"}


def _write_cells(folder: Path, model: str, cells: list[tuple[str, str, dict, dict]]) -> None:
    """cells: (question_id, task, metrics, source). ``metrics`` without outcome = unscored."""
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / "scores.jsonl").open("w", encoding="utf-8") as scores, (folder / "answers.jsonl").open(
        "w", encoding="utf-8"
    ) as answers:
        for qid, task, metrics, source in cells:
            scores.write(json.dumps({"question_id": qid, "model_id": model, "task": task, "metrics": metrics}) + "\n")
            question = {"id": qid, "task": task, "prompt": f"prompt {qid}", "expected": {"text": f"exp {qid}"},
                        "source": source}
            answers.write(
                json.dumps({"question_id": qid, "model_id": model, "task": task, "answer": f"ans {qid}",
                            "question": question}, ensure_ascii=False) + "\n"
            )


def _metrics(outcome: str, task: str = "retrieve_quote", **extra) -> dict:
    base = {"exact": 0, "normalized": 0, "contains_reference": 0, "correct": int(outcome == "correct")}
    if task == "verify_source":
        base = {"parsed": "yes", "expected": "yes", "correct": int(outcome == "correct")}
    if task == "cite_passage":
        base = {"correct": int(outcome == "correct"), "n_candidates": 1}
    return {**base, **extra, "outcome": outcome}


@pytest.fixture
def run(tmp_path: Path) -> Path:
    """Two models, two texts (one holding two works), mixed outcomes, a small stratum and an unscored row."""
    run_dir = tmp_path / "runs" / "test-run"
    quran = _source("The Qur'an", "Uthmani", "ar")
    for model in ("m1", "m2"):
        # 12 correct retrieve_quote cells on islam/native/prompt-native: a stratum larger than k=5.
        rows = [(f"{model}q{i}", "retrieve_quote", _metrics("correct", exact=1), quran) for i in range(6)]
        _write_cells(run_dir / model / "base" / "islam" / "native" / "population" / "prompt-native", model, rows)
        # 2 refused cite cells on islam/native/prompt-english: a stratum smaller than k (4 total).
        rows = [(f"{model}c{i}", "cite_passage", _metrics("refused", "cite_passage"), quran) for i in range(2)]
        # ... plus one unscored row that must never be drawn.
        rows.append((f"{model}u", "cite_passage", {"correct": 0}, quran))
        _write_cells(run_dir / model / "base" / "islam" / "native" / "population" / "prompt-english", model, rows)
        # encyclicals/english holds two works -> a multi-work text.
        rows = [
            (f"{model}e{i}", "verify_source", _metrics("incorrect", "verify_source"),
             _source("Encyclical A" if i % 2 else "Encyclical B", f"Vatican English {i % 2}", "en"))
            for i in range(4)
        ]
        _write_cells(run_dir / model / "base" / "encyclicals" / "english" / "population", model, rows)
    return run_dir


def _build(run: Path, seed: str = "s1", k: int = 5) -> dict:
    return build_sample(run, seed, k, sample_id="test", root=run.parents[1])


def test_same_inputs_give_byte_identical_samples(run: Path) -> None:
    assert dumps_sample(_build(run)) == dumps_sample(_build(run))


def test_a_different_seed_changes_the_draw(run: Path) -> None:
    a = [c["cell_id"] for c in _build(run, seed="s1")["cells"]]
    b = [c["cell_id"] for c in _build(run, seed="s2")["cells"]]
    assert a != b


def test_each_stratum_gives_min_n_k_and_records_its_population(run: Path) -> None:
    sample = _build(run, k=5)
    strata = {(s["outcome"], s["task"], s["text"]): s for s in sample["strata"]}
    assert strata[("correct", "retrieve_quote", "islam/native")] == {
        "drawn": 5, "outcome": "correct", "population": 12, "task": "retrieve_quote", "text": "islam/native"}
    assert strata[("refused", "cite_passage", "islam/native")]["population"] == 4
    assert strata[("refused", "cite_passage", "islam/native")]["drawn"] == 4
    assert strata[("incorrect", "verify_source", "encyclicals/english")]["drawn"] == 5
    drawn = Counter((c["outcome"], c["task"], c["text"]) for c in sample["cells"])
    assert all(drawn[key] == s["drawn"] for key, s in strata.items())
    assert len(sample["cells"]) == sum(s["drawn"] for s in sample["strata"])


def test_unscored_rows_are_never_drawn(run: Path) -> None:
    sample = _build(run, k=100)
    ids = {c["cell_id"] for c in sample["cells"]}
    assert "test-run:m1:m1u" not in ids and "test-run:m2:m2u" not in ids
    assert len(ids) == 2 * (6 + 2 + 4)


def test_cells_carry_ids_paths_and_verbatim_inputs(run: Path) -> None:
    sample = _build(run, k=100)
    cell = next(c for c in sample["cells"] if c["cell_id"] == "test-run:m1:m1q0")
    assert cell["run"] == "test-run" and cell["model_id"] == "m1" and cell["question_id"] == "m1q0"
    assert cell["scores_path"] == "runs/test-run/m1/base/islam/native/population/prompt-native/scores.jsonl"
    assert cell["text"] == "islam/native"
    assert cell["expected"] == {"text": "exp m1q0"} and cell["answer"] == "ans m1q0"
    assert cell["prompt"] == "prompt m1q0" and cell["source"]["language"] == "ar"
    assert cell["outcome"] == "correct" and cell["grader_path"] == "exact"
    assert sample["source_run"] == "runs/test-run"
    assert sample["seed"] == "s1" and sample["per_stratum"] == 100 and sample["sample_id"] == "test"


def test_text_labels_single_and_multi_work(run: Path) -> None:
    texts = {t["id"]: t for t in _build(run, k=100)["texts"]}
    assert texts["islam/native"]["label"] == "The Qur'an — Uthmani"
    assert texts["encyclicals/english"]["label"] == "Encyclicals — 2 works"
    assert texts["islam/native"]["cells"] == 16 and texts["encyclicals/english"]["cells"] == 8


@pytest.mark.parametrize(
    ("task", "metrics", "path"),
    [
        ("retrieve_quote", {"exact": 1, "normalized": 1, "contains_reference": 1}, "exact"),
        ("complete_unit", {"exact": 0, "normalized": 1, "contains_reference": 1}, "normalized"),
        ("retrieve_quote", {"exact": 0, "normalized": 0, "contains_reference": 1}, "contained"),
        ("complete_unit", {"exact": 0, "normalized": 0, "contains_reference": 0}, "none"),
        ("cite_passage", {"correct": 1, "n_candidates": 1}, "citation"),
        ("verify_source", {"parsed": "no", "expected": "no"}, "verdict"),
    ],
)
def test_grader_path_from_recorded_metrics(task: str, metrics: dict, path: str) -> None:
    assert grader_path(task, metrics) == path


def test_a_scored_row_without_an_answer_row_fails_loudly(run: Path) -> None:
    answers = run / "m1" / "base" / "encyclicals" / "english" / "population" / "answers.jsonl"
    lines = answers.read_text(encoding="utf-8").splitlines()
    answers.write_text("\n".join(lines[1:]) + "\n", encoding="utf-8")
    with pytest.raises(ReviewSampleError, match="has no answer row"):
        _build(run)


def test_an_unexpected_layout_fails_loudly(run: Path) -> None:
    _write_cells(run / "m1" / "elsewhere", "m1", [("x", "cite_passage", _metrics("correct", "cite_passage"), {})])
    with pytest.raises(ReviewSampleError, match="expected <run>/<model>/base"):
        _build(run)


def test_load_sample_round_trips_and_rejects_bad_files(run: Path, tmp_path: Path) -> None:
    out = tmp_path / "s.json"
    write_sample(_build(run), out)
    assert load_sample(out)["sample_id"] == "test"
    bad = json.loads(out.read_text(encoding="utf-8"))
    bad["format"] = 2
    out.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(ReviewSampleError, match="unsupported sample format"):
        load_sample(out)
    bad["format"] = 1
    del bad["cells"][0]["answer"]
    out.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(ReviewSampleError, match="missing"):
        load_sample(out)


def test_committed_facct_sample_regenerates_byte_for_byte() -> None:
    """The committed sample is reproducible from committed run evidence, and the run is untouched."""
    run_dir = REPO_ROOT / "runs" / "facct-2026-11-03"
    rebuilt = build_sample(run_dir, COMMITTED_SEED, COMMITTED_K, sample_id=COMMITTED.stem, root=REPO_ROOT)
    assert dumps_sample(rebuilt) == COMMITTED.read_text(encoding="utf-8")
    sample = load_sample(COMMITTED)
    assert len(sample["texts"]) == 13 and len(sample["strata"]) == 151
    assert len(sample["cells"]) == sum(min(s["population"], COMMITTED_K) for s in sample["strata"])
    # Committed (tracked) run evidence is unmodified; untracked in-progress runs don't count.
    changed = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "diff", "--name-only", "HEAD", "--", "runs/"],
        capture_output=True, text=True, check=True,
    ).stdout
    assert changed == ""
