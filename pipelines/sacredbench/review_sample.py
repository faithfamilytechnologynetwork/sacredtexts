"""Draw the review sample: an even, seeded, stratified set of scored cells (Spec 154).

A reviewer who knows a text labels a sample of scored cells with the true outcome, and those
labels become a gold set that any version of the matcher can be scored against. This module
draws that sample from one run directory and writes it as a self-contained JSON file:

- A **cell** is one ``scores.jsonl`` row joined to its ``answers.jsonl`` row on
  ``(model_id, question_id)``. Only rows whose metrics carry an ``outcome`` are eligible.
- A cell's **text** is the edition folder between ``<model>/base/`` and ``population/`` in the
  run layout (``islam/native``, ``encyclicals/english``, …), so grouping is data-driven.
- **Strata** are (outcome, task, text). Each stratum gives ``min(N, k)`` cells, taken in the
  order of ``sha256(seed NUL cell_id)``, so the draw never depends on file-read order.
- The drawn cells are listed in the order of ``sha256(seed NUL "order" NUL cell_id)``.

The run directory is only read. The output is byte-stable for the same run, seed and ``k``.
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path

FORMAT = 1
TASKS = ("retrieve_quote", "complete_unit", "cite_passage", "verify_source")
OUTCOMES = ("correct", "incorrect", "refused")
TOP_KEYS = ("cells", "format", "per_stratum", "sample_id", "seed", "source_run", "strata", "texts")
CELL_KEYS = (
    "answer", "cell_id", "expected", "grader_path", "metrics", "model_id", "outcome", "prompt",
    "question_id", "run", "scores_path", "source", "task", "text",
)


class ReviewSampleError(Exception):
    """The run or a sample file does not have the shape the review sample needs."""


def grader_path(task: str, metrics: dict) -> str:
    """Which grader gave the recorded verdict, read from the recorded submetrics."""
    if task in ("retrieve_quote", "complete_unit"):
        if metrics.get("exact"):
            return "exact"
        if metrics.get("normalized"):
            return "normalized"
        if metrics.get("contains_reference"):
            return "contained"
        return "none"
    if task == "cite_passage":
        return "citation"
    if task == "verify_source":
        return "verdict"
    raise ReviewSampleError(f"unknown task {task!r}")


def _text_id(scores_path: Path, run_dir: Path) -> str:
    """The edition folder of ``<run>/<model>/base/<text...>/population/.../scores.jsonl``."""
    parts = scores_path.relative_to(run_dir).parts
    if len(parts) < 5 or parts[1] != "base" or "population" not in parts[3:]:
        raise ReviewSampleError(
            f"{scores_path}: expected <run>/<model>/base/<edition>/population/.../scores.jsonl"
        )
    return "/".join(parts[2 : parts.index("population", 3)])


def _read_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def _key_rows(rows: list[dict], path: Path) -> dict[tuple[str, str], dict]:
    keyed: dict[tuple[str, str], dict] = {}
    for row in rows:
        key = (row["model_id"], row["question_id"])
        if key in keyed:
            raise ReviewSampleError(f"{path}: duplicate row for model {key[0]!r} question {key[1]!r}")
        keyed[key] = row
    return keyed


def _text_label(text_id: str, works: set[tuple[str, str]]) -> str:
    if len(works) == 1:
        work, version = next(iter(works))
        return f"{work} — {version}"
    tradition = text_id.split("/", 1)[0].replace("-", " ").capitalize()
    return f"{tradition} — {len(works)} works"


def _rank(seed: str, *parts: str) -> str:
    return hashlib.sha256("\x00".join((seed, *parts)).encode("utf-8")).hexdigest()


def load_cells(run_dir: Path, root: Path) -> tuple[list[dict], dict[str, set[tuple[str, str]]]]:
    """Every eligible cell in ``run_dir``, plus the (work, version) pairs seen per text."""
    run_dir = Path(run_dir)
    root = Path(root).resolve()
    try:
        run_rel = run_dir.resolve().relative_to(root)
    except ValueError as exc:
        raise ReviewSampleError(f"run directory {run_dir} is not under {root}") from exc
    run_name = run_dir.resolve().name
    score_files = sorted(run_dir.resolve().rglob("scores.jsonl"))
    if not score_files:
        raise ReviewSampleError(f"{run_dir}: no scores.jsonl files")

    cells: list[dict] = []
    works: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for scores_path in score_files:
        text_id = _text_id(scores_path, run_dir.resolve())
        answers_path = scores_path.with_name("answers.jsonl")
        if not answers_path.is_file():
            raise ReviewSampleError(f"{scores_path}: no answers.jsonl beside it")
        answers = _key_rows(_read_jsonl(answers_path), answers_path)
        rel_scores = (run_rel / scores_path.relative_to(run_dir.resolve())).as_posix()
        for score in _read_jsonl(scores_path):
            key = (score["model_id"], score["question_id"])
            answer = answers.get(key)
            if answer is None:
                raise ReviewSampleError(
                    f"{scores_path}: scored row model {key[0]!r} question {key[1]!r} has no answer row"
                )
            metrics = score["metrics"]
            outcome = metrics.get("outcome")
            if outcome is None:
                continue
            if outcome not in OUTCOMES:
                raise ReviewSampleError(f"{scores_path}: unknown outcome {outcome!r}")
            question = answer["question"]
            source = question["source"]
            works[text_id].add((source["work"], source["version"]))
            cells.append(
                {
                    "answer": answer["answer"],
                    "cell_id": f"{run_name}:{score['model_id']}:{score['question_id']}",
                    "expected": question["expected"],
                    "grader_path": grader_path(score["task"], metrics),
                    "metrics": metrics,
                    "model_id": score["model_id"],
                    "outcome": outcome,
                    "prompt": question["prompt"],
                    "question_id": score["question_id"],
                    "run": run_name,
                    "scores_path": rel_scores,
                    "source": source,
                    "task": score["task"],
                    "text": text_id,
                }
            )
    return cells, works


def build_sample(run_dir: Path, seed: str, per_stratum: int, sample_id: str, root: Path) -> dict:
    """Draw ``min(N, per_stratum)`` cells from every (outcome, task, text) stratum of ``run_dir``."""
    if per_stratum < 1:
        raise ReviewSampleError(f"per_stratum must be at least 1, got {per_stratum}")
    if not seed:
        raise ReviewSampleError("seed must be a non-empty string")
    cells, works = load_cells(run_dir, root)
    if not cells:
        raise ReviewSampleError(f"{run_dir}: no scored cells")

    strata: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    seen: set[str] = set()
    for cell in cells:
        if cell["cell_id"] in seen:
            raise ReviewSampleError(f"duplicate cell {cell['cell_id']}")
        seen.add(cell["cell_id"])
        strata[(cell["outcome"], cell["task"], cell["text"])].append(cell)

    drawn: list[dict] = []
    strata_rows: list[dict] = []
    for key in sorted(strata):
        members = sorted(strata[key], key=lambda c: (_rank(seed, c["cell_id"]), c["cell_id"]))
        take = members[: min(len(members), per_stratum)]
        drawn.extend(take)
        outcome, task, text = key
        strata_rows.append(
            {"drawn": len(take), "outcome": outcome, "population": len(members), "task": task, "text": text}
        )
    drawn.sort(key=lambda c: (_rank(seed, "order", c["cell_id"]), c["cell_id"]))

    drawn_per_text: dict[str, int] = defaultdict(int)
    for cell in drawn:
        drawn_per_text[cell["text"]] += 1
    texts = [
        {"cells": drawn_per_text[text_id], "id": text_id, "label": _text_label(text_id, works[text_id])}
        for text_id in sorted(drawn_per_text)
    ]
    run_rel = Path(run_dir).resolve().relative_to(Path(root).resolve()).as_posix()
    return {
        "cells": drawn,
        "format": FORMAT,
        "per_stratum": per_stratum,
        "sample_id": sample_id,
        "seed": seed,
        "source_run": run_rel,
        "strata": strata_rows,
        "texts": texts,
    }


def dumps_sample(sample: dict) -> str:
    """The canonical, byte-stable serialization of a sample."""
    return json.dumps(sample, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def write_sample(sample: dict, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(dumps_sample(sample), encoding="utf-8")


def load_sample(path: Path) -> dict:
    """Read and validate a sample file; any shape problem fails loudly."""
    try:
        sample = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReviewSampleError(f"{path}: cannot read sample ({exc})") from exc
    if not isinstance(sample, dict):
        raise ReviewSampleError(f"{path}: a sample is a JSON object")
    if sample.get("format") != FORMAT:
        raise ReviewSampleError(f"{path}: unsupported sample format {sample.get('format')!r}")
    missing = [k for k in TOP_KEYS if k not in sample]
    if missing:
        raise ReviewSampleError(f"{path}: missing keys {missing}")
    text_ids = {t["id"] for t in sample["texts"]}
    seen: set[str] = set()
    for cell in sample["cells"]:
        absent = [k for k in CELL_KEYS if k not in cell]
        if absent:
            raise ReviewSampleError(f"{path}: cell {cell.get('cell_id')!r} is missing {absent}")
        if cell["task"] not in TASKS:
            raise ReviewSampleError(f"{path}: cell {cell['cell_id']} has unknown task {cell['task']!r}")
        if cell["outcome"] not in OUTCOMES:
            raise ReviewSampleError(f"{path}: cell {cell['cell_id']} has unknown outcome {cell['outcome']!r}")
        if cell["text"] not in text_ids:
            raise ReviewSampleError(f"{path}: cell {cell['cell_id']} names unknown text {cell['text']!r}")
        if cell["cell_id"] in seen:
            raise ReviewSampleError(f"{path}: duplicate cell {cell['cell_id']}")
        seen.add(cell["cell_id"])
    return sample
