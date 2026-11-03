"""The paper scripts read one run dir and stop when a run row has no question to join (#102).

    uv run --project pipelines --with tqdm pytest items/for-test/test_paper_join.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "pipelines"))

import claim_tests  # noqa: E402
import facct_findings  # noqa: E402

QUESTIONS = Path(__file__).resolve().parent / "islam" / "native" / "population" / "prompt-native" / "questions.jsonl"
FOLDER = Path("islam") / "native" / "population" / "prompt-native"
STALE_ID = "0000000000000000"


def _write(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def _run(tmp_path: Path, extra_ids: list[str]) -> Path:
    """One model, two real questions, plus answers for ids the question files do not have."""
    real = [json.loads(line) for line in QUESTIONS.read_text(encoding="utf-8").splitlines()[:2]]
    questions = real + [dict(real[0], id=qid) for qid in extra_ids]
    dest = tmp_path / "rerun" / "haiku" / "base" / FOLDER
    _write(dest / "answers.jsonl", [
        {"question_id": q["id"], "model_id": "haiku", "task": q["task"], "answer": "x", "question": q}
        for q in questions
    ])
    _write(dest / "scores.jsonl", [
        {"question_id": q["id"], "task": q["task"], "metrics": {"outcome": "incorrect"}} for q in questions
    ])
    return tmp_path / "rerun"


@pytest.mark.parametrize("script", [claim_tests, facct_findings])
def test_unmatched_id_aborts_with_the_numbers(script, tmp_path, monkeypatch):
    out = tmp_path / "paper" / "out.md"
    monkeypatch.setattr(script, "OUT", out)
    run_dir = _run(tmp_path, [STALE_ID])
    with pytest.raises(SystemExit, match=r"2 of 3") as exc:
        script.main(run_dir=str(run_dir))
    assert "haiku: 2/3" in str(exc.value.code)
    assert not out.exists()


@pytest.mark.parametrize("script", [claim_tests, facct_findings])
def test_run_dir_without_answers_is_refused(script, tmp_path):
    (tmp_path / "empty").mkdir()
    with pytest.raises(SystemExit, match="no answers.jsonl"):
        script.main(run_dir=str(tmp_path / "empty"))
    with pytest.raises(SystemExit, match="not a directory"):
        script.main(run_dir=str(tmp_path / "missing"))


def test_allow_partial_writes_the_report_and_says_what_was_left_out(tmp_path, monkeypatch):
    out = tmp_path / "paper" / "claim-tests.md"
    monkeypatch.setattr(claim_tests, "OUT", out)
    claim_tests.main(run_dir=str(_run(tmp_path, [STALE_ID])), allow_partial=True)
    header = out.read_text(encoding="utf-8").splitlines()[2]
    assert header.startswith("From 2 scored cells across 1 models in ")
    assert "1 of 3 answer rows have no question" in header


def test_full_coverage_reads_only_the_run_dir(tmp_path, monkeypatch):
    out = tmp_path / "paper" / "claim-tests.md"
    monkeypatch.setattr(claim_tests, "OUT", out)
    claim_tests.main(run_dir=str(_run(tmp_path, [])))
    header = out.read_text(encoding="utf-8").splitlines()[2]
    assert header.startswith("From 2 scored cells across 1 models in ")
    assert "no question" not in header
