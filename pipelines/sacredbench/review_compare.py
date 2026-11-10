"""Score matcher versions against human labels (Spec 154).

A **gold set** is a JSONL file of human labels, one row per labelled cell, downloaded from the
review tool. Each row carries everything needed to re-score its cell (task, prompt, expected,
answer, source), the verdict the matcher showed at labelling time (``shown``), and the human
``label``. So a gold set does not depend on any one matcher version.

A **version** is a source of verdicts for the gold rows:

- ``committed``: the run's recorded scores, read now from each row's ``scores_path``;
- ``current``: a re-score by the scorer code in this checkout (``score.score_answer``, default
  graders, exactly as ``sacredbench score`` calls it). No network;
- a **run directory** with the layout of ``runs/<run>/``, for example a copy re-scored on another
  branch. A row's ``scores_path`` has its ``runs/<run>/`` prefix replaced by the directory.

For each version the report gives agreement with the human (``agree / n``) overall, per task,
per text and per grader path, and lists the disagreements. ``cant_judge`` and defect-flagged rows
are not in ``n``; they are counted on their own line. With two or more versions the first is the
baseline, and each other version lists its **movers**: judged cells whose outcome changed, marked
``fixed`` (now agrees with the human), ``broken`` (no longer agrees) or ``neither``. Movers are
taken over the same judged rows as agreement, so ``agree(version) - agree(baseline)`` is always
``fixed - broken``.
"""

from __future__ import annotations

import json
import math
import uuid
from collections import defaultdict
from datetime import datetime
from pathlib import Path, PurePosixPath

from sacredbench.review_sample import OUTCOMES, TASKS, grader_path
from sacredbench.score import score_answer

GOLD_FORMAT = 1
REPORT_FORMAT = 1
LABEL_OUTCOMES = ("correct", "incorrect", "refused", "cant_judge")
GOLD_KEYS = (
    "answer", "cell_id", "expected", "format", "label", "labelled_at", "model_id", "prompt",
    "question_id", "reviewer_id", "rubric_version", "run", "sample_id", "scores_path", "shown",
    "source", "task", "text",
)
SHOWN_KEYS = ("grader_path", "metrics", "outcome")
LABEL_KEYS = ("defect", "notes", "outcome")
# Sample-cell fields copied into a gold row unchanged.
CELL_FIELDS = (
    "answer", "cell_id", "expected", "model_id", "prompt", "question_id", "run", "scores_path",
    "source", "task", "text",
)
COMMITTED = "committed"
CURRENT = "current"
MOVER_KINDS = ("fixed", "broken", "neither")
NO_ARM = "(none)"


class ReviewCompareError(Exception):
    """A gold set or a version cannot be read as the comparison needs."""


# --- gold-set rows -------------------------------------------------------------------------------


def gold_row(
    cell: dict, *, sample_id: str, label: dict, reviewer_id: str, labelled_at: str, rubric_version: str
) -> dict:
    """The gold row for one labelled sample cell (the review UI builds the same row)."""
    row = {key: cell[key] for key in CELL_FIELDS}
    row.update(
        format=GOLD_FORMAT,
        label={key: label[key] for key in LABEL_KEYS},
        labelled_at=labelled_at,
        reviewer_id=reviewer_id,
        rubric_version=rubric_version,
        sample_id=sample_id,
        shown={"grader_path": cell["grader_path"], "metrics": cell["metrics"], "outcome": cell["outcome"]},
    )
    return row


def _js_number(value: float) -> int | float:
    """A float as ``JSON.stringify`` writes it: ``1.0`` becomes ``1``. Fails where Python's
    shortest form would differ from JavaScript's (exponent notation below 1e-4)."""
    if not math.isfinite(value):
        raise ReviewCompareError(f"cannot write non-finite number {value!r} to a gold set")
    if value.is_integer():
        if abs(value) >= 1e21:
            raise ReviewCompareError(f"cannot write {value!r} identically to JSON.stringify")
        return int(value)
    if abs(value) < 1e-4:
        raise ReviewCompareError(f"cannot write {value!r} identically to JSON.stringify")
    return value


def _canonical(value):
    if isinstance(value, dict):
        return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_canonical(item) for item in value]
    if isinstance(value, float):
        return _js_number(value)
    return value


def dumps_gold_rows(rows: list[dict]) -> str:
    """The canonical gold-set bytes: rows sorted by ``(cell_id, reviewer_id)``, one compact JSON
    object per line, keys sorted at every level, non-ASCII unescaped, numbers as JSON.stringify
    writes them. The review UI's download is byte-identical to this."""
    ordered = sorted(rows, key=lambda r: (r["cell_id"], r["reviewer_id"]))
    return "".join(
        json.dumps(_canonical(row), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for row in ordered
    )


def _require_str(row: dict, key: str, where: str, *, allow_empty: bool = False) -> None:
    value = row[key]
    if not isinstance(value, str) or (not allow_empty and not value):
        raise ReviewCompareError(f"{where}: {key!r} must be a {'' if allow_empty else 'non-empty '}string")


def _require_keys(group: object, keys: tuple[str, ...], name: str, where: str) -> None:
    if not isinstance(group, dict):
        raise ReviewCompareError(f"{where}: {name!r} must be an object")
    missing = [k for k in keys if k not in group]
    if missing:
        raise ReviewCompareError(f"{where}: {name!r} is missing {missing}")
    unknown = sorted(set(group) - set(keys))
    if unknown:
        raise ReviewCompareError(f"{where}: {name!r} has unknown fields {unknown}")


def _validate_gold_row(row: object, where: str) -> None:
    if not isinstance(row, dict):
        raise ReviewCompareError(f"{where}: a gold row is a JSON object")
    if row.get("format") != GOLD_FORMAT:
        raise ReviewCompareError(f"{where}: unknown gold-set format {row.get('format')!r}")
    _require_keys(row, GOLD_KEYS, "row", where)
    for key in ("cell_id", "model_id", "prompt", "question_id", "reviewer_id", "rubric_version", "run",
                "sample_id", "scores_path", "task", "text", "labelled_at"):
        _require_str(row, key, where)
    _require_str(row, "answer", where, allow_empty=True)
    if row["task"] not in TASKS:
        raise ReviewCompareError(f"{where}: unknown task {row['task']!r}")
    if row["cell_id"] != f"{row['run']}:{row['model_id']}:{row['question_id']}":
        raise ReviewCompareError(f"{where}: cell_id {row['cell_id']!r} is not <run>:<model_id>:<question_id>")
    scores_path = PurePosixPath(row["scores_path"])
    if scores_path.is_absolute() or ".." in scores_path.parts:
        raise ReviewCompareError(
            f"{where}: scores_path {row['scores_path']!r} must be relative to the repo root, without '..'"
        )
    for key in ("expected", "source"):
        if not isinstance(row[key], dict):
            raise ReviewCompareError(f"{where}: {key!r} must be an object")

    shown = row["shown"]
    _require_keys(shown, SHOWN_KEYS, "shown", where)
    if shown["outcome"] not in OUTCOMES:
        raise ReviewCompareError(f"{where}: unknown shown outcome {shown['outcome']!r}")
    if not isinstance(shown["metrics"], dict) or not isinstance(shown["grader_path"], str):
        raise ReviewCompareError(f"{where}: shown metrics must be an object and grader_path a string")

    label = row["label"]
    _require_keys(label, LABEL_KEYS, "label", where)
    if label["outcome"] not in LABEL_OUTCOMES:
        raise ReviewCompareError(
            f"{where}: unknown label outcome {label['outcome']!r} (expected one of {list(LABEL_OUTCOMES)})"
        )
    if not isinstance(label["defect"], bool):
        raise ReviewCompareError(f"{where}: label defect must be true or false")
    if not isinstance(label["notes"], str):
        raise ReviewCompareError(f"{where}: label notes must be a string")

    try:
        uuid.UUID(row["reviewer_id"])
    except ValueError as exc:
        raise ReviewCompareError(f"{where}: reviewer_id {row['reviewer_id']!r} is not a UUID") from exc
    try:
        stamp = datetime.fromisoformat(row["labelled_at"])
    except ValueError as exc:
        raise ReviewCompareError(f"{where}: labelled_at {row['labelled_at']!r} is not ISO 8601") from exc
    if stamp.tzinfo is None:
        raise ReviewCompareError(f"{where}: labelled_at {row['labelled_at']!r} has no time zone")


def load_gold(paths: list[Path]) -> list[dict]:
    """Read and validate gold-set files; any problem fails loudly. Rows come back sorted by
    ``(cell_id, reviewer_id)``. A ``(reviewer_id, cell_id)`` labelled twice, in one file or across
    files, is an error."""
    if not paths:
        raise ReviewCompareError("no gold-set files given")
    rows: list[dict] = []
    first_seen: dict[tuple[str, str], str] = {}
    for path in paths:
        try:
            lines = Path(path).read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            raise ReviewCompareError(f"{path}: cannot read gold set ({exc})") from exc
        previous_cell = ""
        for line_no, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            where = f"{path}:{line_no}"
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ReviewCompareError(f"{where}: not JSON ({exc})") from exc
            _validate_gold_row(row, where)
            key = (row["reviewer_id"], row["cell_id"])
            if key in first_seen:
                raise ReviewCompareError(
                    f"{where}: reviewer {key[0]} labelled cell {key[1]} twice (first at {first_seen[key]})"
                )
            first_seen[key] = where
            if row["cell_id"] < previous_cell:
                raise ReviewCompareError(
                    f"{where}: rows are not sorted by cell_id (pass each downloaded gold set as its own "
                    "argument rather than concatenating files)"
                )
            previous_cell = row["cell_id"]
            rows.append(row)
    if not rows:
        raise ReviewCompareError(f"no gold rows in {[str(p) for p in paths]}")
    rows.sort(key=lambda r: (r["cell_id"], r["reviewer_id"]))
    return rows


# --- versions ------------------------------------------------------------------------------------


def _index_scores(path: Path, version: str) -> dict[tuple[str, str], dict]:
    if not path.is_file():
        raise ReviewCompareError(f"version {version!r}: scores file {path} not found")
    keyed: dict[tuple[str, str], dict] = {}
    with path.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ReviewCompareError(f"{path}:{line_no}: not JSON ({exc})") from exc
            if not isinstance(row, dict) or not all(k in row for k in ("model_id", "question_id", "metrics")):
                raise ReviewCompareError(f"{path}:{line_no}: a scores row needs model_id, question_id and metrics")
            key = (row["model_id"], row["question_id"])
            if key in keyed:
                raise ReviewCompareError(
                    f"version {version!r}: {path} has more than one row for model {key[0]!r} question {key[1]!r}"
                )
            keyed[key] = row
    return keyed


def _scored_metrics(rows: list[dict], paths: list[Path], version: str) -> list[dict]:
    """Each gold row's metrics from the scores file at the matching path."""
    indexes: dict[Path, dict[tuple[str, str], dict]] = {}
    metrics: list[dict] = []
    for row, path in zip(rows, paths):
        if path not in indexes:
            indexes[path] = _index_scores(path, version)
        scored = indexes[path].get((row["model_id"], row["question_id"]))
        if scored is None:
            raise ReviewCompareError(
                f"version {version!r}: {path} has no row for cell {row['cell_id']} "
                f"(model {row['model_id']!r}, question {row['question_id']!r})"
            )
        if scored.get("task") != row["task"]:
            raise ReviewCompareError(
                f"version {version!r}: {path} scores cell {row['cell_id']} as task {scored.get('task')!r}, "
                f"but the gold row is {row['task']!r}"
            )
        metrics.append(scored["metrics"])
    return metrics


def _rescored_metrics(rows: list[dict]) -> list[dict]:
    """Re-score each row as ``score.score_file`` does: default graders, language/prompt/work."""
    return [
        score_answer(
            row["task"], row["answer"], row["expected"],
            language=row["source"].get("language"), prompt=row["prompt"], work=row["source"].get("work"),
        )
        for row in rows
    ]


def _run_dir_paths(rows: list[dict], run_dir: Path, version: str) -> list[Path]:
    runs = sorted({row["run"] for row in rows})
    if len(runs) > 1:
        raise ReviewCompareError(
            f"version {version!r}: the gold rows come from more than one run {runs}, so a run directory "
            "is ambiguous; compare one run's gold rows at a time"
        )
    prefix = f"runs/{runs[0]}/"
    paths: list[Path] = []
    for row in rows:
        if not row["scores_path"].startswith(prefix):
            raise ReviewCompareError(
                f"version {version!r}: cell {row['cell_id']} scores_path {row['scores_path']!r} "
                f"does not start with {prefix!r}"
            )
        paths.append(run_dir / row["scores_path"][len(prefix):])
    return paths


def version_metrics(version: str, rows: list[dict], root: Path) -> list[dict]:
    """One metrics dict per gold row, from ``committed``, ``current`` or a run directory."""
    if version == COMMITTED:
        metrics = _scored_metrics(rows, [Path(root) / row["scores_path"] for row in rows], version)
    elif version == CURRENT:
        metrics = _rescored_metrics(rows)
    else:
        run_dir = Path(version)
        if not run_dir.is_dir():
            raise ReviewCompareError(
                f"version {version!r} is not {COMMITTED!r}, {CURRENT!r} or an existing run directory"
            )
        metrics = _scored_metrics(rows, _run_dir_paths(rows, run_dir, version), version)
    for row, m in zip(rows, metrics):
        if m.get("outcome") not in OUTCOMES:
            raise ReviewCompareError(
                f"version {version!r}: cell {row['cell_id']} has no valid outcome ({m.get('outcome')!r})"
            )
    return metrics


# --- comparison ----------------------------------------------------------------------------------


def _judged(row: dict) -> bool:
    return row["label"]["outcome"] != "cant_judge" and not row["label"]["defect"]


def _tally(agree: int, n: int) -> dict:
    return {"agree": agree, "n": n, "pct": round(100 * agree / n, 1) if n else None}


def _breakdown(keys: list[str], agrees: list[bool]) -> dict[str, dict]:
    groups: dict[str, list[bool]] = defaultdict(list)
    for key, agree in zip(keys, agrees):
        groups[key].append(agree)
    return {key: _tally(sum(groups[key]), len(groups[key])) for key in sorted(groups)}


def _version_report(version: str, rows: list[dict], metrics: list[dict]) -> dict:
    judged = [i for i, row in enumerate(rows) if _judged(row)]
    outcomes = [m["outcome"] for m in metrics]
    agrees = [outcomes[i] == rows[i]["label"]["outcome"] for i in judged]
    by_text = _breakdown([rows[i]["text"] for i in judged], agrees)
    arms: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for i in judged:
        arms[rows[i]["text"]][rows[i]["source"].get("condition") or NO_ARM] += 1
    for text, tally in by_text.items():
        tally["arms"] = dict(sorted(arms[text].items()))
    return {
        "version": version,
        "rows": len(rows),
        "excluded": {
            "cant_judge": sum(row["label"]["outcome"] == "cant_judge" for row in rows),
            "defect": sum(row["label"]["defect"] for row in rows),
            "total": len(rows) - len(judged),
        },
        "overall": _tally(sum(agrees), len(judged)),
        "by_task": _breakdown([rows[i]["task"] for i in judged], agrees),
        "by_text": by_text,
        "by_grader_path": _breakdown([grader_path(rows[i]["task"], metrics[i]) for i in judged], agrees),
        "disagreements": [
            {
                "cell_id": rows[i]["cell_id"],
                "human": rows[i]["label"]["outcome"],
                "reviewer_id": rows[i]["reviewer_id"],
                "task": rows[i]["task"],
                "text": rows[i]["text"],
                "version": outcomes[i],
            }
            for i, agree in zip(judged, agrees)
            if not agree
        ],
    }


def _movers(baseline: str, base: list[dict], version: str, other: list[dict], rows: list[dict]) -> dict:
    cells = []
    for i, row in enumerate(rows):
        if not _judged(row) or base[i]["outcome"] == other[i]["outcome"]:
            continue
        human = row["label"]["outcome"]
        if other[i]["outcome"] == human:
            kind = "fixed"
        elif base[i]["outcome"] == human:
            kind = "broken"
        else:
            kind = "neither"
        cells.append(
            {
                "baseline": base[i]["outcome"],
                "cell_id": row["cell_id"],
                "human": human,
                "kind": kind,
                "reviewer_id": row["reviewer_id"],
                "task": row["task"],
                "text": row["text"],
                "version": other[i]["outcome"],
            }
        )
    return {
        "baseline": baseline,
        "version": version,
        "counts": {kind: sum(c["kind"] == kind for c in cells) for kind in MOVER_KINDS},
        "cells": cells,
    }


def compare(rows: list[dict], versions: list[str], root: Path) -> dict:
    """The comparison report for ``rows`` (from ``load_gold``) under each version, in order.
    ``root`` is the directory ``scores_path`` is relative to (the repo root)."""
    if not versions:
        raise ReviewCompareError("give at least one version")
    repeated = sorted({v for v in versions if versions.count(v) > 1})
    if repeated:
        raise ReviewCompareError(f"version(s) given more than once: {repeated}")
    metrics = {version: version_metrics(version, rows, root) for version in versions}
    baseline = versions[0]
    return {
        "format": REPORT_FORMAT,
        "rows": len(rows),
        "reviewers": sorted({row["reviewer_id"] for row in rows}),
        "versions": [_version_report(version, rows, metrics[version]) for version in versions],
        "movers": [
            _movers(baseline, metrics[baseline], version, metrics[version], rows) for version in versions[1:]
        ],
    }


# --- output --------------------------------------------------------------------------------------


def dumps_report(report: dict) -> str:
    return json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def _fmt_tally(tally: dict) -> str:
    pct = "—" if tally["pct"] is None else f"{tally['pct']:.1f}%"
    return f"{tally['agree']} / {tally['n']} ({pct})"


def _table(rows: list[tuple[str, str]], indent: str = "  ") -> list[str]:
    if not rows:
        return [f"{indent}(no judged rows)"]
    width = max(len(key) for key, _ in rows)
    return [f"{indent}{key.ljust(width)}  {value}".rstrip() for key, value in rows]


def format_report(report: dict) -> str:
    """The plain-text report (deterministic)."""
    many_reviewers = len(report["reviewers"]) > 1

    def who(cell: dict) -> str:
        return f"  reviewer={cell['reviewer_id']}" if many_reviewers else ""

    names = [v["version"] for v in report["versions"]]
    lines = [
        f"gold rows: {report['rows']} from {len(report['reviewers'])} reviewer(s); versions: {', '.join(names)}",
    ]
    for v in report["versions"]:
        ex = v["excluded"]
        lines += [
            "",
            f"== {v['version']} ==",
            f"judged {v['overall']['n']}; excluded {ex['total']} (cant_judge {ex['cant_judge']}, defect {ex['defect']})",
            f"overall: {_fmt_tally(v['overall'])}",
            "by task:",
            *_table([(k, _fmt_tally(t)) for k, t in v["by_task"].items()]),
            "by text:",
            *_table(
                [
                    (k, f"{_fmt_tally(t)}  arms: " + ", ".join(f"{arm} {n}" for arm, n in t["arms"].items()))
                    for k, t in v["by_text"].items()
                ]
            ),
            "by grader path:",
            *_table([(k, _fmt_tally(t)) for k, t in v["by_grader_path"].items()]),
            f"disagreements: {len(v['disagreements'])}",
        ]
        lines += [
            f"  {d['cell_id']}  {d['task']}  {d['text']}  human={d['human']}  {v['version']}={d['version']}{who(d)}"
            for d in v["disagreements"]
        ]
    for m in report["movers"]:
        counts = m["counts"]
        lines += [
            "",
            f"== movers: {m['version']} vs {m['baseline']} ==",
            ", ".join(f"{kind} {counts[kind]}" for kind in MOVER_KINDS),
        ]
        lines += [
            f"  {c['kind'].ljust(7)}  {c['cell_id']}  {c['task']}  {c['text']}  human={c['human']}  "
            f"{m['baseline']}={c['baseline']}  {m['version']}={c['version']}{who(c)}"
            for c in m["cells"]
        ]
    return "\n".join(lines) + "\n"
