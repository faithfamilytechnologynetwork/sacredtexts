"""Spec 154 phase 2: gold-set rows and the version comparison (review-compare).

The shared fixture (``fixtures/review_sample.json`` + ``fixtures/review_gold_set.jsonl``) is 10 cells:
every task in ``islam/native`` (Arabic, RTL) and in ``hinduism/english``. Its ``shown`` verdicts
stand for the committed scores at labelling time. Two of them are an older matcher's:

- the ``islam/native`` cite cell answers ``34:46 أو 3:140`` (an undisclaimed echo of the form example
  beside the right verse). Shown ``incorrect`` (two candidates); the current matcher drops the echo and
  says ``correct``; the human says ``incorrect``, so ``current`` **breaks** it;
- the ``hinduism/english`` retrieve cell answers ``Yogi`` for ``Yogî``. Shown ``incorrect``; the current
  matcher folds English diacritics (#94) and says ``correct``; the human agrees, so ``current`` **fixes** it.

The ``islam/native`` retrieve cell is correct by containment but hedges between two verses, so the human
says ``incorrect`` under every version. Two ``verify_source`` cells are judged (a refusal that never opens
with Yes/No, and a "Yes" to a false premise); two more are ``cant_judge`` and defect-flagged.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from sacredbench.review_compare import (
    CELL_FIELDS,
    ReviewCompareError,
    compare,
    dumps_gold_rows,
    dumps_report,
    format_report,
    gold_row,
    load_gold,
)
from sacredbench.review_sample import load_sample
from sacredbench.review_service import fetch_gold_set, service_base

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_SAMPLE = REPO_ROOT / "fixtures" / "review_sample.json"
FIXTURE_GOLD = REPO_ROOT / "fixtures" / "review_gold_set.jsonl"
FIXTURE_RESULTS = REPO_ROOT / "fixtures" / "review_results.json"
COMMITTED_SAMPLE = REPO_ROOT / "review" / "samples" / "facct-2026-11-03-k10.json"
REVIEWER = "3f2b8c1e-5d4a-4e6f-9b7c-1a2d3e4f5a6b"

AR_RETRIEVE = "fixture-run:model-a:7c41160f85999097"  # contained, human incorrect
AR_CITE = "fixture-run:model-a:12e45dddc647beb6"  # broken by current
AR_VERIFY = "fixture-run:model-b:aeaa707307175fdb"  # cant_judge
AR_REFUSAL = "fixture-run:model-a:aeaa707307175fdb"  # refused, human refused
EN_RETRIEVE = "fixture-run:model-a:b9bdeb4400fc2a64"  # fixed by current
EN_VERIFY = "fixture-run:model-b:1e33ec77e1ed0b3f"  # defect


def _tally(agree: int, n: int) -> dict:
    return {"agree": agree, "n": n, "pct": round(100 * agree / n, 1)}


def _write_scores(target: Path, rows: list[dict], *, prefix: str = "", override: dict | None = None,
                  duplicate: str | None = None, omit: str | None = None,
                  evaluators: tuple[str, ...] = ("strict", "containment")) -> None:
    """A scores stand-in: each row's ``shown.metrics`` at ``target/<scores_path minus prefix>``, with a
    ``summary.json`` beside it recording ``evaluators``. ``override`` replaces metrics by cell id;
    ``duplicate`` writes that cell's row twice; ``omit`` leaves that cell's row out of its (still
    written) file."""
    by_path: dict[Path, list[str]] = {}
    for row in rows:
        metrics = (override or {}).get(row["cell_id"], row["shown"]["metrics"])
        line = json.dumps({"question_id": row["question_id"], "model_id": row["model_id"], "task": row["task"],
                           "metrics": metrics}, ensure_ascii=False) + "\n"
        path = target / row["scores_path"][len(prefix):]
        copies = 0 if row["cell_id"] == omit else 2 if row["cell_id"] == duplicate else 1
        by_path.setdefault(path, []).append(line * copies)
    for path, lines in by_path.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(lines), encoding="utf-8")
        # The run summary beside each scores file records the graders it was scored with.
        (path.parent / "summary.json").write_text(json.dumps({"evaluators": list(evaluators)}), encoding="utf-8")


def _write_gold(path: Path, rows: list[dict]) -> Path:
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    return path


@pytest.fixture
def gold() -> list[dict]:
    return load_gold([FIXTURE_GOLD])


@pytest.fixture
def root(tmp_path: Path, gold: list[dict]) -> Path:
    """A repo-root stand-in whose runs/fixture-run holds the committed (shown) scores."""
    _write_scores(tmp_path, gold)
    return tmp_path


def _version(report: dict, name: str) -> dict:
    return next(v for v in report["versions"] if v["version"] == name)


# --- the shared fixture --------------------------------------------------------------------------


def test_fixture_gold_rows_are_the_sample_cells_labelled() -> None:
    sample = load_sample(FIXTURE_SAMPLE)
    cells = {c["cell_id"]: c for c in sample["cells"]}
    rows = load_gold([FIXTURE_GOLD])
    assert len(rows) == len(cells) == 10
    assert {c["task"] for c in cells.values()} == {"retrieve_quote", "complete_unit", "cite_passage", "verify_source"}
    assert {c["text"] for c in cells.values()} == {"islam/native", "hinduism/english"}
    for row in rows:
        cell = cells[row["cell_id"]]
        assert {k: row[k] for k in CELL_FIELDS} == {k: cell[k] for k in CELL_FIELDS}
        assert row["shown"] == {"grader_path": cell["grader_path"], "metrics": cell["metrics"], "outcome": cell["outcome"]}
        assert row["sample_id"] == sample["sample_id"] and row["reviewer_id"] == REVIEWER


def test_fixture_gold_set_is_canonical_and_rebuilds_from_the_sample() -> None:
    """The Python side of the UI parity contract: sample cells + labels give these exact bytes."""
    sample = load_sample(FIXTURE_SAMPLE)
    rows = {r["cell_id"]: r for r in load_gold([FIXTURE_GOLD])}
    rebuilt = [
        gold_row(cell, sample_id=sample["sample_id"], label=rows[cell["cell_id"]]["label"],
                 reviewer_id=REVIEWER, labelled_at=rows[cell["cell_id"]]["labelled_at"], rubric_version="1")
        for cell in sample["cells"]
    ]
    text = FIXTURE_GOLD.read_text(encoding="utf-8")
    assert dumps_gold_rows(rebuilt) == text
    assert '"token_f1":1,' in text and '"token_f1": 1.0' in FIXTURE_SAMPLE.read_text(encoding="utf-8")


def test_gold_numbers_are_written_as_json_stringify_writes_them() -> None:
    row = load_gold([FIXTURE_GOLD])[0]
    row["shown"]["metrics"] = {"a": 1.0, "b": 0.5778, "c": -0.0, "d": 0, "e": 0.0001}
    assert '"metrics":{"a":1,"b":0.5778,"c":0,"d":0,"e":0.0001}' in dumps_gold_rows([row])
    for bad in (1e-05, float("nan"), 1e21):
        row["shown"]["metrics"] = {"x": bad}
        with pytest.raises(ReviewCompareError, match="cannot write"):
            dumps_gold_rows([row])


# --- the comparison on the fixture ---------------------------------------------------------------


def test_committed_counts_match_the_hand_computed_numbers(gold: list[dict], root: Path) -> None:
    v = compare(gold, ["committed"], root)["versions"][0]
    assert v["rows"] == 10
    assert v["excluded"] == {"both": 0, "cant_judge": 1, "defect": 1, "total": 2}
    assert v["overall"] == _tally(6, 8)
    assert v["by_task"] == {
        "cite_passage": _tally(2, 2), "complete_unit": _tally(2, 2), "retrieve_quote": _tally(0, 2),
        "verify_source": _tally(2, 2),
    }
    assert v["by_text"] == {
        "hinduism/english": {**_tally(3, 4), "arms": {"en_ask_en_answer": 4}},
        "islam/native": {**_tally(3, 4), "arms": {"ask_english": 2, "ask_native": 2}},
    }
    assert v["by_grader_path"] == {
        "citation": _tally(2, 2), "contained": _tally(0, 1), "exact": _tally(1, 1), "none": _tally(1, 2),
        "verdict": _tally(2, 2),
    }
    assert [(d["cell_id"], d["human"], d["version"]) for d in v["disagreements"]] == [
        (AR_RETRIEVE, "incorrect", "correct"), (EN_RETRIEVE, "correct", "incorrect"),
    ]


def test_committed_matches_the_results_page_fixture(gold: list[dict], root: Path) -> None:
    """The review tool's results page counts the shown verdicts as ``committed`` does (issue #157):
    the viewer's vitest pins its numbers to the same file."""
    v = compare(gold, ["committed"], root)["versions"][0]
    del v["version"]
    for tally in v["by_text"].values():
        del tally["arms"]
    assert v == json.loads(FIXTURE_RESULTS.read_text(encoding="utf-8"))


def test_current_rescores_with_the_real_scorer(gold: list[dict], root: Path) -> None:
    v = compare(gold, ["current"], root)["versions"][0]
    assert v["overall"] == _tally(6, 8)
    assert v["by_task"] == {
        "cite_passage": _tally(1, 2), "complete_unit": _tally(2, 2), "retrieve_quote": _tally(1, 2),
        "verify_source": _tally(2, 2),
    }
    assert v["by_text"]["hinduism/english"] == {**_tally(4, 4), "arms": {"en_ask_en_answer": 4}}
    assert v["by_text"]["islam/native"] == {**_tally(2, 4), "arms": {"ask_english": 2, "ask_native": 2}}
    assert v["by_grader_path"] == {
        "citation": _tally(1, 2), "contained": _tally(0, 1), "exact": _tally(1, 1), "none": _tally(1, 1),
        "normalized": _tally(1, 1), "verdict": _tally(2, 2),
    }
    rows = {r["cell_id"]: r for r in gold}
    assert rows[AR_REFUSAL]["label"]["outcome"] == "refused" and AR_REFUSAL not in {d["cell_id"] for d in v["disagreements"]}
    assert [(d["cell_id"], d["version"]) for d in v["disagreements"]] == [(AR_CITE, "correct"), (AR_RETRIEVE, "correct")]


def test_movers_against_the_baseline_are_fixed_and_broken(gold: list[dict], root: Path) -> None:
    report = compare(gold, ["committed", "current"], root)
    (movers,) = report["movers"]
    assert (movers["baseline"], movers["version"]) == ("committed", "current")
    assert movers["counts"] == {"fixed": 1, "broken": 1, "neither": 0}
    assert [(c["cell_id"], c["kind"], c["baseline"], c["version"], c["human"]) for c in movers["cells"]] == [
        (AR_CITE, "broken", "incorrect", "correct", "incorrect"),
        (EN_RETRIEVE, "fixed", "incorrect", "correct", "correct"),
    ]
    agree = [v["overall"]["agree"] for v in report["versions"]]
    assert agree[1] - agree[0] == movers["counts"]["fixed"] - movers["counts"]["broken"]


def test_a_single_version_has_no_movers(gold: list[dict], root: Path) -> None:
    assert compare(gold, ["current"], root)["movers"] == []


def test_cant_judge_and_defect_rows_are_counted_apart(gold: list[dict], root: Path, tmp_path: Path) -> None:
    rows = [dict(r, label=dict(r["label"])) for r in gold]
    for row in rows:
        if row["cell_id"] == AR_VERIFY:
            row["label"]["defect"] = True  # cant_judge AND defect: one excluded row
        if row["cell_id"] == EN_RETRIEVE:
            row["label"]["outcome"] = "cant_judge"
    v = compare(load_gold([_write_gold(tmp_path / "g.jsonl", rows)]), ["committed"], root)["versions"][0]
    assert v["excluded"] == {"both": 1, "cant_judge": 2, "defect": 2, "total": 3}
    assert v["overall"] == _tally(6, 7)
    assert EN_RETRIEVE not in {d["cell_id"] for d in v["disagreements"]}


# --- run-directory versions ----------------------------------------------------------------------


def test_a_run_directory_resolves_through_the_run_prefix_swap(gold: list[dict], root: Path, tmp_path: Path) -> None:
    version_b = tmp_path / "rescored-elsewhere"
    rows = {r["cell_id"]: r for r in gold}
    _write_scores(version_b, gold, prefix="runs/fixture-run/", override={
        AR_RETRIEVE: {**rows[AR_RETRIEVE]["shown"]["metrics"], "correct": 0, "outcome": "refused"},
        EN_RETRIEVE: {**rows[EN_RETRIEVE]["shown"]["metrics"], "normalized": 1, "correct": 1, "outcome": "correct"},
    })
    report = compare(gold, ["committed", str(version_b)], root)
    v = _version(report, str(version_b))
    assert v["overall"] == _tally(7, 8)
    assert v["by_grader_path"]["normalized"] == _tally(1, 1)
    (movers,) = report["movers"]
    assert movers["counts"] == {"fixed": 1, "broken": 0, "neither": 1}
    assert [(c["cell_id"], c["kind"]) for c in movers["cells"]] == [(AR_RETRIEVE, "neither"), (EN_RETRIEVE, "fixed")]


def test_current_fails_on_a_run_scored_with_non_default_graders(gold: list[dict], tmp_path: Path) -> None:
    _write_scores(tmp_path, gold, evaluators=("strict",))
    with pytest.raises(ReviewCompareError, match=r"scored with evaluators \['strict'\].*default graders"):
        compare(gold, ["current"], tmp_path)
    # committed and a run directory read recorded verdicts, so they are not affected
    assert compare(gold, ["committed"], tmp_path)["versions"][0]["overall"]["n"] == 8


def test_current_accepts_the_default_graders_in_any_order(gold: list[dict], tmp_path: Path) -> None:
    _write_scores(tmp_path, gold, evaluators=("containment", "strict"))
    assert compare(gold, ["current"], tmp_path)["versions"][0]["overall"]["agree"] == 6


def test_current_fails_when_the_run_summary_is_missing(gold: list[dict], root: Path) -> None:
    next(root.rglob("summary.json")).unlink()
    with pytest.raises(ReviewCompareError, match="summary.json not found, so the graders"):
        compare(gold, ["current"], root)


def test_a_run_directory_over_two_runs_is_ambiguous(gold: list[dict], root: Path, tmp_path: Path) -> None:
    other = dict(gold[0], run="other-run", cell_id=gold[0]["cell_id"].replace("fixture-run", "other-run", 1))
    mixed = sorted(gold + [other], key=lambda r: r["cell_id"])
    rows = load_gold([_write_gold(tmp_path / "g.jsonl", mixed)])
    with pytest.raises(ReviewCompareError, match="more than one run"):
        compare(rows, [str(root / "runs" / "fixture-run")], root)


def test_a_run_directory_needs_the_runs_prefix(gold: list[dict], root: Path, tmp_path: Path) -> None:
    rows = [dict(r, scores_path=r["scores_path"].replace("runs/", "elsewhere/", 1)) for r in gold]
    with pytest.raises(ReviewCompareError, match="is not a path under 'runs/fixture-run/'"):
        compare(rows, [str(root / "runs" / "fixture-run")], root)


def test_a_run_directory_lookup_never_leaves_the_directory(gold: list[dict], root: Path) -> None:
    """Even a row that skipped the loader's canonical-path check resolves inside the directory."""
    run_dir = root / "runs" / "fixture-run"
    rows = [dict(gold[0], scores_path="runs/fixture-run//etc/passwd")]
    with pytest.raises(ReviewCompareError, match=f"scores file {run_dir}/etc/passwd not found"):
        compare(rows, [str(run_dir)], root)
    rows = [dict(gold[0], scores_path="runs/fixture-run/../../outside/scores.jsonl")]
    with pytest.raises(ReviewCompareError, match="is not a path under 'runs/fixture-run/'"):
        compare(rows, [str(run_dir)], root)


@pytest.mark.parametrize("as_directory", [False, True])
def test_a_duplicate_key_in_a_scores_file_fails(gold: list[dict], tmp_path: Path, as_directory: bool) -> None:
    _write_scores(tmp_path, gold, duplicate=AR_CITE)
    version = str(tmp_path / "runs" / "fixture-run") if as_directory else "committed"
    with pytest.raises(ReviewCompareError, match="more than one row for model 'model-a' question '12e45dddc647beb6'"):
        compare(gold, [version], tmp_path)


def test_a_missing_committed_file_or_row_fails(gold: list[dict], tmp_path: Path) -> None:
    with pytest.raises(ReviewCompareError, match="scores file .* not found"):
        compare(gold, ["committed"], tmp_path)
    _write_scores(tmp_path, gold, omit=AR_CITE)
    with pytest.raises(ReviewCompareError, match=f"has no row for cell {AR_CITE}"):
        compare(gold, ["committed"], tmp_path)


def test_unknown_and_repeated_versions_fail(gold: list[dict], root: Path) -> None:
    with pytest.raises(ReviewCompareError, match="not 'committed', 'current' or an existing run directory"):
        compare(gold, ["comitted"], root)
    with pytest.raises(ReviewCompareError, match="more than once"):
        compare(gold, ["current", "current"], root)
    with pytest.raises(ReviewCompareError, match="at least one version"):
        compare(gold, [], root)


# --- the gold-set loader -------------------------------------------------------------------------


def _mutate(row: dict, change: str) -> None:
    if change == "format":
        row["format"] = 2
    elif change == "missing":
        del row["answer"]
    elif change == "extra":
        row["email"] = "someone@example.org"
    elif change == "label_outcome":
        row["label"]["outcome"] = "partly"
    elif change == "defect":
        row["label"]["defect"] = "no"
    elif change == "reviewer":
        row["reviewer_id"] = "reviewer-1"
    elif change == "labelled_at":
        row["labelled_at"] = "yesterday"
    elif change == "naive_time":
        row["labelled_at"] = "2026-11-10T12:00:00"
    elif change == "cell_id":
        row["cell_id"] = row["cell_id"] + "x"
    elif change == "task":
        row["task"] = "summarise"
    elif change == "shown":
        row["shown"]["outcome"] = "cant_judge"
    elif change == "escape":
        row["scores_path"] = "runs/fixture-run/../../etc/scores.jsonl"
    elif change == "absolute":
        row["scores_path"] = "/etc/scores.jsonl"
    elif change == "doubled_slash":
        row["scores_path"] = "runs/fixture-run//etc/passwd"
    elif change == "dot":
        row["scores_path"] = "runs/./fixture-run/model-a/scores.jsonl"
    elif change == "expected_key":
        row["expected"] = {"unrelated": "x"}


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ("format", "unknown gold-set format 2"),
        ("missing", r"'row' is missing \['answer'\]"),
        ("extra", r"'row' has unknown fields \['email'\]"),
        ("label_outcome", "unknown label outcome 'partly'"),
        ("defect", "defect must be true or false"),
        ("reviewer", "is not a UUID"),
        ("labelled_at", "is not ISO 8601"),
        ("naive_time", "has no time zone"),
        ("cell_id", "is not <run>:<model_id>:<question_id>"),
        ("task", "unknown task 'summarise'"),
        ("shown", "unknown shown outcome 'cant_judge'"),
        ("escape", "must be a canonical path relative to the repo root"),
        ("absolute", "must be a canonical path relative to the repo root"),
        ("doubled_slash", "must be a canonical path relative to the repo root"),
        ("dot", "must be a canonical path relative to the repo root"),
        ("expected_key", r"row needs a string expected\.(text|citation|answer)"),
    ],
)
def test_the_loader_rejects_a_bad_row(tmp_path: Path, change: str, message: str) -> None:
    rows = [json.loads(line) for line in FIXTURE_GOLD.read_text(encoding="utf-8").splitlines()]
    _mutate(rows[3], change)
    path = _write_gold(tmp_path / "g.jsonl", rows)
    with pytest.raises(ReviewCompareError, match=message) as err:
        load_gold([path])
    assert f"{path}:4" in str(err.value)


def test_a_duplicate_label_across_files_fails(tmp_path: Path) -> None:
    copy = tmp_path / "copy.jsonl"
    shutil.copy(FIXTURE_GOLD, copy)
    with pytest.raises(ReviewCompareError, match=f"reviewer {REVIEWER} labelled cell .* twice"):
        load_gold([FIXTURE_GOLD, copy])


def test_unsorted_rows_fail(tmp_path: Path) -> None:
    rows = FIXTURE_GOLD.read_text(encoding="utf-8").splitlines()
    path = tmp_path / "g.jsonl"
    path.write_text("\n".join(reversed(rows)) + "\n", encoding="utf-8")
    with pytest.raises(ReviewCompareError, match="not sorted by cell_id .*rather than concatenating"):
        load_gold([path])


def test_two_reviewers_of_one_cell_are_both_counted(gold: list[dict], root: Path, tmp_path: Path) -> None:
    second = "9d1e2f3a-4b5c-4d6e-8f70-1a2b3c4d5e6f"
    other = _write_gold(tmp_path / "other.jsonl", [dict(r, reviewer_id=second) for r in gold])
    report = compare(load_gold([FIXTURE_GOLD, other]), ["committed"], root)
    assert report["rows"] == 20 and report["reviewers"] == sorted([REVIEWER, second])
    assert report["versions"][0]["overall"] == _tally(12, 16)
    assert f"reviewer={second}" in format_report(report)


# --- output and the CLI --------------------------------------------------------------------------


def test_the_text_report_is_deterministic(gold: list[dict], root: Path) -> None:
    text = format_report(compare(gold, ["committed", "current"], root))
    assert text == format_report(compare(gold, ["committed", "current"], root))
    assert "overall: 6 / 8 (75.0%)" in text
    assert "judged 8; excluded 2 (cant_judge 1, defect 1, both 0)" in text
    assert "islam/native      3 / 4 (75.0%)  arms: ask_english 2, ask_native 2" in text
    assert "== movers: current vs committed ==\nfixed 1, broken 1, neither 0" in text
    assert f"  broken   {AR_CITE}  cite_passage  islam/native  human=incorrect  committed=incorrect  current=correct" in text


def test_the_cli_prints_the_report_and_writes_the_same_numbers_as_json(
    gold: list[dict], root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from typer.testing import CliRunner

    from sacredbench.cli import app

    monkeypatch.chdir(root)
    args = ["review-compare", str(FIXTURE_GOLD), "--version", "committed", "--version", "current",
            "--json", "out/report.json"]
    first = CliRunner().invoke(app, args)
    assert first.exit_code == 0, first.output
    report = compare(gold, ["committed", "current"], root)
    assert first.output == format_report(report)
    written = (root / "out" / "report.json").read_text(encoding="utf-8")
    assert written == dumps_report(report)
    assert json.loads(written)["movers"][0]["counts"] == {"fixed": 1, "broken": 1, "neither": 0}
    second = CliRunner().invoke(app, args)
    assert second.output == first.output and (root / "out" / "report.json").read_text(encoding="utf-8") == written


def test_the_cli_refuses_to_write_json_under_runs(root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from typer.testing import CliRunner

    from sacredbench.cli import app

    monkeypatch.chdir(root)
    result = CliRunner().invoke(
        app, ["review-compare", str(FIXTURE_GOLD), "--version", "committed", "--json", "runs/report.json"]
    )
    assert isinstance(result.exception, ReviewCompareError)
    assert not (root / "runs" / "report.json").exists()


@pytest.mark.parametrize("case", ["missing_row", "duplicate_label", "unknown_format"])
def test_errors_exit_non_zero_with_a_clear_message(gold: list[dict], tmp_path: Path, case: str) -> None:
    """The real entry point: ``python -m sacredbench`` prints ``error: …`` and exits 2."""
    files = [str(FIXTURE_GOLD)]
    if case == "missing_row":
        _write_scores(tmp_path, gold, omit=AR_CITE)
        message = f"has no row for cell {AR_CITE}"
    elif case == "duplicate_label":
        _write_scores(tmp_path, gold)
        files.append(str(FIXTURE_GOLD))
        message = "labelled cell .* twice"
    else:
        _write_scores(tmp_path, gold)
        rows = [json.loads(line) for line in FIXTURE_GOLD.read_text(encoding="utf-8").splitlines()]
        rows[0]["format"] = 9
        files = [str(_write_gold(tmp_path / "g.jsonl", rows))]
        message = "unknown gold-set format 9"
    proc = subprocess.run(
        [sys.executable, "-m", "sacredbench", "review-compare", *files, "--version", "committed"],
        cwd=tmp_path, capture_output=True, text=True,
    )
    assert proc.returncode == 2
    assert proc.stdout == ""
    assert re.search(f"^error: .*{message}", proc.stderr), proc.stderr


def test_current_makes_no_network_calls_and_imports_no_provider(root: Path) -> None:
    tmp_path = root
    script = f"""
import socket, sys
def refuse(*args, **kwargs):
    raise AssertionError("network call attempted")
socket.socket.connect = refuse
socket.create_connection = refuse
from pathlib import Path
from sacredbench.review_compare import compare, load_gold
report = compare(load_gold([Path({str(FIXTURE_GOLD)!r})]), ["current"], Path({str(tmp_path)!r}))
assert report["versions"][0]["overall"]["agree"] == 6, report["versions"][0]["overall"]
loaded = sorted(m for m in sys.modules if m == "sacredbench.providers" or m.split(".")[0] in
                {{"anthropic", "openai", "google", "httpx", "requests"}})
assert not loaded, loaded
print("ok")
"""
    proc = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == "ok"


def test_the_real_entrypoint_rescores_offline_without_a_provider_sdk(root: Path) -> None:
    """``python -m sacredbench review-compare --version current`` with sockets refused and every
    provider SDK blocked from loading. (The CLI module itself imports ``sacredbench.providers`` for
    the collect/score commands; that module loads no SDK and opens no connection on import.)"""
    script = f"""
import runpy, socket, sys
class BlockProviderSdks:
    def find_spec(self, name, path=None, target=None):
        if name.split(".")[0] in {{"anthropic", "openai", "httpx", "requests"}} or name.startswith("google.genai"):
            raise ImportError("provider SDK import attempted: " + name)
sys.meta_path.insert(0, BlockProviderSdks())
def refuse(*args, **kwargs):
    raise AssertionError("network call attempted")
socket.socket.connect = refuse
socket.create_connection = refuse
sys.argv = ["sacredbench", "review-compare", {str(FIXTURE_GOLD)!r}, "--version", "current"]
runpy.run_module("sacredbench", run_name="__main__")
"""
    proc = subprocess.run([sys.executable, "-c", script], cwd=root, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert "== current ==" in proc.stdout and "overall: 6 / 8 (75.0%)" in proc.stdout


def test_smoke_first_20_committed_sample_cells_agree_with_themselves(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The CLI from the repo root on labels equal to what was shown: committed agrees 100%, and
    current moves nothing."""
    from typer.testing import CliRunner

    from sacredbench.cli import app

    sample = load_sample(COMMITTED_SAMPLE)
    rows = [
        gold_row(cell, sample_id=sample["sample_id"], label={"outcome": cell["outcome"], "defect": False, "notes": ""},
                 reviewer_id=REVIEWER, labelled_at="2026-11-10T00:00:00Z", rubric_version="1")
        for cell in sample["cells"][:20]
    ]
    path = tmp_path / "gold.jsonl"
    path.write_text(dumps_gold_rows(rows), encoding="utf-8")
    monkeypatch.chdir(REPO_ROOT)
    result = CliRunner().invoke(
        app, ["review-compare", str(path), "--version", "committed", "--version", "current", "--json",
              str(tmp_path / "report.json")]
    )
    assert result.exit_code == 0, result.output
    assert result.output.count("overall: 20 / 20 (100.0%)") == 2
    assert "disagreements: 0" in result.output and "fixed 0, broken 0, neither 0" in result.output
    report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    assert [v["overall"] for v in report["versions"]] == [_tally(20, 20)] * 2
    assert report["movers"][0]["cells"] == []


# --- --from-service: the gold set from the review service (issue #157) ----------------------------

EMAIL, PASSWORD = "rev@example.com", "a-secret-passphrase"


class _FakeService(BaseHTTPRequestHandler):
    """The review service's login, gold-set and logout endpoints. ``mode`` breaks one of them."""

    gold = b""
    mode = "ok"
    calls: list[str] = []

    def log_message(self, *args) -> None:
        pass

    def _reply(self, status: int, body: bytes, content_type: str, cookies: tuple[str, ...] = ()) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        for cookie in cookies:
            self.send_header("Set-Cookie", cookie)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        body = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        self.calls.append(f"POST {self.path}")
        if self.path == "/api/auth/login" and self.mode == "html":
            self._reply(200, b"<!doctype html><html></html>", "text/html")
        elif self.path == "/api/auth/login" and json.loads(body) != {"email": EMAIL, "password": PASSWORD}:
            self._reply(401, b'{"error":"invalid credentials"}', "application/json")
        elif self.path == "/api/auth/login":
            self._reply(200, b'{"csrfToken":"csrf-1","reviewer":{}}', "application/json", (
                "st_session=tok-1; Path=/; HttpOnly; Secure; SameSite=None",
                "st_csrf=csrf-1; Path=/; Secure; SameSite=None",
            ))
        elif self.headers["X-CSRF-Token"] == "csrf-1" and "st_csrf=csrf-1" in self.headers["Cookie"]:
            self._reply(200, b'{"ok":true}', "application/json")  # logout
        else:
            self._reply(403, b'{"error":"csrf"}', "application/json")

    def do_GET(self) -> None:
        self.calls.append(f"GET {self.path}")
        if self.path == "/api/gold-set" and "st_session=tok-1" in self.headers["Cookie"]:
            self._reply(200, b"" if self.mode == "empty" else self.gold, "application/jsonl; charset=utf-8")
        else:
            self._reply(401, b'{"error":"unauthorized"}', "application/json")


@pytest.fixture
def service():
    handler = type("Handler", (_FakeService,), {"gold": FIXTURE_GOLD.read_bytes(), "mode": "ok", "calls": []})
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield handler, f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    server.server_close()


def test_from_service_reports_exactly_as_the_downloaded_file_does(
    gold: list[dict], root: Path, service, monkeypatch: pytest.MonkeyPatch
) -> None:
    from typer.testing import CliRunner

    from sacredbench.cli import app

    handler, base = service
    monkeypatch.chdir(root)
    monkeypatch.setenv("REVIEW_EMAIL", EMAIL)
    monkeypatch.setenv("REVIEW_PASSWORD", PASSWORD)
    files_before = sorted(root.rglob("*"))
    result = CliRunner().invoke(
        app, ["review-compare", "--from-service", f"{base}/", "--version", "committed", "--version", "current"]
    )
    assert result.exit_code == 0, result.output
    assert result.output == format_report(compare(gold, ["committed", "current"], root))
    assert handler.calls == ["POST /api/auth/login", "GET /api/gold-set", "POST /api/auth/logout"]
    assert not any(secret in result.output for secret in (EMAIL, PASSWORD, "tok-1", "csrf-1"))
    assert sorted(root.rglob("*")) == files_before


def test_from_service_prompts_for_unset_credentials_and_hides_the_password(
    root: Path, service, monkeypatch: pytest.MonkeyPatch
) -> None:
    from typer.testing import CliRunner

    from sacredbench.cli import app

    _, base = service
    monkeypatch.chdir(root)
    monkeypatch.delenv("REVIEW_EMAIL", raising=False)
    monkeypatch.delenv("REVIEW_PASSWORD", raising=False)
    result = CliRunner().invoke(
        app, ["review-compare", "--from-service", base, "--version", "committed"], input=f"{EMAIL}\n{PASSWORD}\n"
    )
    assert result.exit_code == 0, result.output
    assert "overall: 6 / 8 (75.0%)" in result.output and PASSWORD not in result.output


@pytest.mark.parametrize(("mode", "password", "message"), [
    ("ok", "wrong-password", r"login to http://127\.0\.0\.1:\d+ failed \(401: invalid credentials\)"),
    ("html", PASSWORD, r"answered 200 with text/html, not JSON"),
    ("empty", PASSWORD, r"is empty: this account has no labelled cells"),
])
def test_from_service_fails_loudly(service, mode: str, password: str, message: str) -> None:
    handler, base = service
    handler.mode = mode
    with pytest.raises(ReviewCompareError, match=message) as failure:
        fetch_gold_set(base, EMAIL, password)
    assert password not in str(failure.value) and EMAIL not in str(failure.value)
    if mode == "empty":  # the session it opened is closed again
        assert handler.calls[-1] == "POST /api/auth/logout"


def test_a_failed_login_exits_non_zero_without_printing_credentials(root: Path, service) -> None:
    _, base = service
    env = {**os.environ, "REVIEW_EMAIL": EMAIL, "REVIEW_PASSWORD": "wrong-password"}
    proc = subprocess.run(
        [sys.executable, "-m", "sacredbench", "review-compare", "--from-service", base, "--version", "committed"],
        cwd=root, env=env, capture_output=True, text=True,
    )
    assert proc.returncode == 2 and proc.stdout == ""
    assert re.search(r"^error: login to .* failed \(401: invalid credentials\)", proc.stderr), proc.stderr
    assert "wrong-password" not in proc.stderr and EMAIL not in proc.stderr


def test_the_service_must_be_https_off_this_machine() -> None:
    for url in ("http://review.example.com", "ftp://localhost/", "localhost:8080"):
        with pytest.raises(ReviewCompareError, match="must be https://"):
            service_base(url)
    assert service_base("https://review.example.com/") == "https://review.example.com"
    assert service_base("http://localhost:8080/") == "http://localhost:8080"


def test_review_compare_takes_files_or_a_service_exactly_one(root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from typer.testing import CliRunner

    from sacredbench.cli import app

    monkeypatch.chdir(root)
    for args in ([str(FIXTURE_GOLD), "--from-service", "https://review.example.com"], []):
        result = CliRunner().invoke(app, ["review-compare", *args, "--version", "committed"])
        assert isinstance(result.exception, ReviewCompareError), result.output
