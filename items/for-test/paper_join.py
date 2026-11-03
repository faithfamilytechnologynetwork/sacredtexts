"""Read one run dir and join its rows to the population question files, or stop.

A model folder keeps answers, not the question file, so the paper scripts join each
row to ``items/for-test/**/population/**/questions.jsonl`` by ``question_id``. When the
question sets are regenerated, old ids stop matching. A row that does not match is
left out of every table that needs the question, so a run collected on an older
question set must stop the script, not shrink it.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
# Top-level runs/ names that hold no model (same set as join_run.RESERVED_RUN_NAMES).
NOT_MODELS = frozenset({"panel", "paper", "archive"})


def resolve_run_dir(arg: str) -> Path:
    """The run root holding ``<model>/base/**``, such as ``runs/rerun-2026-11-03``. Relative to the repo root."""
    run_dir = Path(arg)
    if not run_dir.is_absolute():
        run_dir = REPO / run_dir
    run_dir = run_dir.resolve()
    if not run_dir.is_dir():
        raise SystemExit(f"--run-dir {run_dir} is not a directory")
    if not any(model_files(run_dir, "answers.jsonl")):
        raise SystemExit(f"no answers.jsonl under {run_dir}/<model>/base/")
    return run_dir


def model_files(run_dir: Path, name: str):
    """``(model, path)`` for every ``<run-dir>/<model>/base/**/<name>``."""
    for path in sorted(run_dir.glob(f"*/base/**/{name}")):
        model = path.relative_to(run_dir).parts[0]
        if model not in NOT_MODELS:
            yield model, path


def rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def population_questions() -> dict[str, dict]:
    """Every population question row, by id."""
    index: dict[str, dict] = {}
    for path in ROOT.rglob("questions.jsonl"):
        if "population" in path.parts:
            for row in rows(path):
                index[row["id"]] = row
    return index


def check_coverage(run_dir: Path, questions: dict[str, dict], allow_partial: bool) -> tuple[int, int]:
    """Matched and total answer rows. Stops unless every row has a question or ``allow_partial`` is set."""
    counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for model, path in model_files(run_dir, "answers.jsonl"):
        for row in rows(path):
            counts[model][0] += row["question_id"] in questions
            counts[model][1] += 1
    matched = sum(m for m, _ in counts.values())
    total = sum(t for _, t in counts.values())
    if matched == total:
        return matched, total
    report = "\n".join(f"  {model}: {m}/{t}" for model, (m, t) in sorted(counts.items()) if m < t)
    message = (
        f"{matched} of {total} answer rows in {run_dir} match a population question in {ROOT}.\n"
        f"{report}\n"
        "These answers were collected on a different question set. Point --run-dir at a run "
        "collected on the current question files, or pass --allow-partial to drop the rest."
    )
    if not allow_partial:
        raise SystemExit(message)
    print(f"--allow-partial: {message}", file=sys.stderr)
    return matched, total


def partial_note(matched: int, total: int) -> str:
    if matched == total:
        return ""
    return (
        f" {total - matched} of {total} answer rows have no question in the current files;"
        " every table that joins to the question files leaves them out (--allow-partial)."
    )
