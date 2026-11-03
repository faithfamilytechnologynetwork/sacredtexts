"""The paper figures read one required run dir, not every runs/<model>/base/ (#107).

    uv run --project pipelines --with tqdm pytest items/for-test/test_paper_figures.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import typer
from typer.testing import CliRunner

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "pipelines"))

import paper_figures  # noqa: E402

QUESTIONS = Path(__file__).resolve().parent / "islam" / "native" / "population" / "prompt-native" / "questions.jsonl"
FOLDER = Path("islam") / "native" / "population" / "prompt-native"
QUESTION = json.loads(QUESTIONS.read_text(encoding="utf-8").splitlines()[0])
STALE_ID = "0000000000000000"


def _model(root: Path, model: str, answer: str, incorrect: int, extra_ids: tuple[str, ...] = ()) -> None:
    """One retrieve_quote answer per id, plus the finished file's summary.json."""
    dest = root / model / "base" / FOLDER
    dest.mkdir(parents=True)
    answers = [
        {"question_id": qid, "model_id": model, "task": QUESTION["task"], "answer": answer, "question": QUESTION}
        for qid in (QUESTION["id"], *extra_ids)
    ]
    (dest / "answers.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in answers), encoding="utf-8")
    summary = {"models": {model: {QUESTION["task"]: {"correct": 0, "incorrect": incorrect, "refused": 0}}}}
    (dest / "summary.json").write_text(json.dumps(summary), encoding="utf-8")


@pytest.fixture
def out(tmp_path, monkeypatch) -> Path:
    path = tmp_path / "paper"
    monkeypatch.setattr(paper_figures, "OUT", path)
    return path


@pytest.fixture
def runs(tmp_path) -> Path:
    """The archive layout runs/<model>/base/ with a rerun root beside it, as on main."""
    root = tmp_path / "runs"
    _model(root, "haiku", "x", incorrect=1)
    _model(root / "rerun-2026-11-03", "haiku", QUESTION["expected"]["text"], incorrect=7)
    return root


def _haiku_task_row(out: Path) -> str:
    return next(line for line in (out / "models-by-task.tex").read_text(encoding="utf-8").splitlines() if line.startswith("haiku &"))


def _row_with(accuracy: str) -> str:
    """The haiku row with ``accuracy`` in QUESTION's task column and a dash in the others."""
    cells = ["---"] * len(paper_figures.TASKS)
    cells[paper_figures.TASKS.index(QUESTION["task"])] = accuracy
    return "haiku & " + " & ".join(cells) + r" \\"


def test_refuses_without_run_dir(out):
    app = typer.Typer()
    app.command()(paper_figures.main)
    result = CliRunner().invoke(app, [])
    assert result.exit_code == 2
    assert "--run-dir" in result.output
    assert not out.exists()


def test_reads_only_the_given_run_dir(runs, out):
    paper_figures.main(run_dir=str(runs / "rerun-2026-11-03"))
    # The rerun answer is the verse, so its task is 100; the archive answer beside it would be 0.
    assert _haiku_task_row(out) == _row_with("100.0")
    early = (out / "early-outcomes.md").read_text(encoding="utf-8")
    assert "| haiku | Islam | retrieve_quote | 7 | 0.0% | 100.0% | 0 |" in early
    assert f"From {runs / 'rerun-2026-11-03'}." in (out / "models-by-tradition.tex").read_text(encoding="utf-8")


def test_unmatched_id_aborts_before_writing(tmp_path, out):
    _model(tmp_path / "rerun", "haiku", QUESTION["expected"]["text"], incorrect=0, extra_ids=(STALE_ID,))
    with pytest.raises(SystemExit, match=r"1 of 2") as exc:
        paper_figures.main(run_dir=str(tmp_path / "rerun"))
    assert "haiku: 1/2" in str(exc.value.code)
    assert not out.exists()


def test_allow_partial_leaves_the_unmatched_row_out_and_says_so(tmp_path, out):
    _model(tmp_path / "rerun", "haiku", QUESTION["expected"]["text"], incorrect=0, extra_ids=(STALE_ID,))
    paper_figures.main(run_dir=str(tmp_path / "rerun"), allow_partial=True)
    assert _haiku_task_row(out) == _row_with("100.0")
    assert "1 of 2 answer rows have no question" in (out / "models-by-task.tex").read_text(encoding="utf-8")


def test_model_not_on_the_panel_is_refused(tmp_path, out):
    _model(tmp_path / "rerun", "not-a-panel-model", "x", incorrect=1)
    with pytest.raises(SystemExit, match="not-a-panel-model .* is not on the panel"):
        paper_figures.main(run_dir=str(tmp_path / "rerun"))
    assert not out.exists()
