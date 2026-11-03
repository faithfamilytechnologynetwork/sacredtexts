"""--run-dir keys every output path on the run dir and never on the committed runs/ archive.

    uv run --project pipelines --with tqdm pytest items/for-test/test_join_run.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import join_run  # noqa: E402

QUESTIONS = join_run.ROOT / "islam" / "native" / "population" / "prompt-native" / "questions.jsonl"


def test_default_is_todays_runs_layout():
    run_dir = join_run.resolve_run_dir(None)
    assert run_dir == join_run.REPO / "runs"
    assert join_run.out_dir("haiku", QUESTIONS, run_dir) == (
        join_run.REPO / "runs" / "haiku" / "base" / "islam" / "native" / "population" / "prompt-native"
    )
    assert join_run._card_path("haiku", run_dir) == join_run.REPO / "runs" / "haiku" / "model.json"


def test_run_dir_moves_answers_and_card():
    run_dir = join_run.resolve_run_dir("runs/rerun-2026-11-03")
    rerun = (join_run.REPO / "runs" / "rerun-2026-11-03").resolve()
    assert run_dir == rerun
    assert join_run.out_dir("haiku", QUESTIONS, run_dir) == (
        rerun / "haiku" / "base" / "islam" / "native" / "population" / "prompt-native"
    )
    assert join_run._card_path("haiku", run_dir) == rerun / "haiku" / "model.json"


def test_run_dir_absolute_path_is_kept(tmp_path):
    assert join_run.resolve_run_dir(str(tmp_path)) == tmp_path.resolve()


@pytest.mark.parametrize(
    "arg",
    ["runs", "runs/", "./runs", "runs/haiku", "runs/haiku/base", "runs/haiku/base/x", "runs/panel", "runs/archive/x"],
)
def test_run_dir_refuses_the_committed_archive(arg):
    with pytest.raises(SystemExit):
        join_run.resolve_run_dir(arg)


def test_seed_card_fails_without_a_committed_card(tmp_path, monkeypatch):
    monkeypatch.setattr(join_run, "RUNS", tmp_path / "runs")
    with pytest.raises(SystemExit, match="model.json"):
        join_run.seed_card("haiku", tmp_path / "rerun")
    assert not (tmp_path / "rerun").exists()


def test_seed_and_reconcile_write_only_under_the_run_dir(tmp_path, monkeypatch):
    committed = tmp_path / "runs"
    (committed / "haiku").mkdir(parents=True)
    card = {
        "panel_id": "haiku",
        "catalogue": {"pricing_usd_per_token": {"prompt": "0.000001", "completion": "0.000002"}},
        "collected": {"calls": 99, "prompt_tokens": 1, "completion_tokens": 1, "cost_usd": 1},
    }
    (committed / "haiku" / "model.json").write_text(json.dumps(card), encoding="utf-8")
    before = (committed / "haiku" / "model.json").read_bytes()
    monkeypatch.setattr(join_run, "RUNS", committed)

    run_dir = tmp_path / "rerun"
    seeded = join_run.seed_card("haiku", run_dir)
    assert seeded == run_dir / "haiku" / "model.json"
    assert "collected" not in json.loads(seeded.read_text(encoding="utf-8"))

    dest = join_run.out_dir("haiku", QUESTIONS, run_dir)
    dest.mkdir(parents=True)
    rows = [
        {"model_id": "haiku", "usage": {"in": 100, "out": 10}},
        {"model_id": "haiku", "usage": {"in": 50, "out": 5}},
    ]
    (dest / "answers.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    totals = join_run.reconcile_usage("haiku", run_dir)
    assert totals == {"calls": 2, "prompt_tokens": 150, "completion_tokens": 15, "cost_usd": 0.00018}
    totals = join_run.add_usage("haiku", {"usage": {"in": 10, "out": 1}}, run_dir)
    assert totals["calls"] == 3

    assert (committed / "haiku" / "model.json").read_bytes() == before
    assert not (committed / "haiku" / "base").exists()
