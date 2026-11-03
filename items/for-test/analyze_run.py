"""FAccT-shaped progress report for one model.

Scores the answers on disk with the same graders as ``sacredbench score``. Writes
``runs/<model>/analysis.md``. This is a preview. The card for a finished folder
is ``python -m sacredbench facct`` on that folder, and it will not accept a
partial file.

    python3 items/for-test/analyze_run.py
    python3 items/for-test/analyze_run.py --model qwen3-32b
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
RUNS = REPO / "runs"
sys.path.insert(0, str(REPO / "pipelines"))

from sacredbench.score import score_answer  # noqa: E402


def _rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _n_questions(rel: Path) -> int | None:
    path = ROOT / rel / "questions.jsonl"
    if not path.exists():
        return None
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def _pct(correct: int, incorrect: int) -> str:
    answered = correct + incorrect
    if not answered:
        return "—"
    return f"{100 * correct / answered:.1f}%"


def _mean(xs: list[float]) -> str:
    if not xs:
        return "—"
    return f"{sum(xs) / len(xs):.3f}"


def report(model: str) -> str:
    base = RUNS / model / "base"
    files = sorted(base.rglob("answers.jsonl")) if base.is_dir() else []
    by_task: dict[str, dict] = defaultdict(lambda: {"correct": 0, "incorrect": 0, "refused": 0, "f1": [], "f1_base": []})
    by_file: list[tuple[str, int, int | None, dict]] = []
    prompt = completion = 0
    hosts: dict[str, int] = defaultdict(int)
    for path in files:
        rows = _rows(path)
        rel = path.parent.relative_to(base)
        file_counts = {"correct": 0, "incorrect": 0, "refused": 0}
        for row in rows:
            question = row.get("question") or {}
            expected = question.get("expected") or {}
            language = (question.get("source") or {}).get("language")
            metrics = score_answer(
                row.get("task") or "", row.get("answer") or "", expected, language=language, prompt=question.get("prompt")
            )
            outcome = metrics.get("outcome") or "incorrect"
            bucket = by_task[row.get("task") or "?"]
            bucket[outcome] += 1
            file_counts[outcome] += 1
            if "token_f1" in metrics and outcome != "refused":
                bucket["f1"].append(float(metrics["token_f1"]))
                bucket["f1_base"].append(float(metrics["token_f1_base"]))
            usage = row.get("usage") or {}
            prompt += int(usage.get("in") or 0)
            completion += int(usage.get("out") or 0)
            if usage.get("provider"):
                hosts[usage["provider"]] += 1
        by_file.append((str(rel), len(rows), _n_questions(rel), file_counts))

    answered = sum(b["correct"] + b["incorrect"] + b["refused"] for b in by_task.values())
    lines = [
        f"# FAccT preview — {model}",
        "",
        "What these answers are allowed to mean. Accuracy is correct divided by correct plus incorrect. "
        "A refusal is left out of accuracy and counted in coverage. `token_f1` is the strict wording "
        "overlap. `token_f1_base` folds script and spelling differences and is a diagnostic, not the headline.",
        "",
        "This file is a preview of the answers on disk. It is not the FAccT card. "
        "`python -m sacredbench facct` writes that card for one finished folder, and it refuses a partial file. "
        "The blank card for the whole panel is `runs/analysis-template.md`.",
        "",
        "## Scope",
        "",
    ]
    if not files:
        lines.append("No answers yet.")
        return "\n".join(lines) + "\n"
    lines += [
        "| file | saved | questions in file | correct | incorrect | refused |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for rel, n, n_q, counts in by_file:
        lines.append(
            f"| `{rel}` | {n} | {n_q if n_q is not None else '—'} | "
            f"{counts['correct']} | {counts['incorrect']} | {counts['refused']} |"
        )
    pending = sum((n_q - n) for _, n, n_q, _ in by_file if n_q is not None)
    lines += [
        "",
        f"{answered} scored answers. {pending} questions in those files are still pending. "
        "Other traditions and the other Christianity files have not been called. "
        "A score on this slice is not a score for Christianity, and not a score for the panel.",
        "",
        "## Outcomes",
        "",
        "| task | n | correct | incorrect | refused | accuracy | token_f1 | token_f1_base |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    total = {"correct": 0, "incorrect": 0, "refused": 0, "f1": [], "f1_base": []}
    for task in sorted(by_task):
        b = by_task[task]
        n = b["correct"] + b["incorrect"] + b["refused"]
        lines.append(
            f"| {task} | {n} | {b['correct']} | {b['incorrect']} | {b['refused']} | "
            f"{_pct(b['correct'], b['incorrect'])} | {_mean(b['f1'])} | {_mean(b['f1_base'])} |"
        )
        for key in ("correct", "incorrect", "refused"):
            total[key] += b[key]
        total["f1"] += b["f1"]
        total["f1_base"] += b["f1_base"]
    lines.append(
        f"| **overall** | {answered} | {total['correct']} | {total['incorrect']} | {total['refused']} | "
        f"**{_pct(total['correct'], total['incorrect'])}** | {_mean(total['f1'])} | {_mean(total['f1_base'])} |"
    )
    lines += [
        "",
        "Cite and verify have no token F1. Those cells are blank on those columns and the overall F1 "
        "is the mean of the quote and completion rows only. On English Latin the two F1s match, "
        "because there is no script or spelling fold to apply. They separate on Hebrew, Greek, Arabic, "
        "Gurmukhi, Devanagari, and romanized Pali.",
        "",
        "## What this does not show",
        "",
        "- One English NRSV file, stopped partway. Masoretic, Greek, and the other five traditions are absent.",
        "- Familiarity is not in this run.",
        "- Search is off. Temperature is 0.",
        "- Reasoning is still on for this model, so output tokens and call time include the hidden trace. Cost is not comparable to a model called without reasoning.",
        "- The edition counterfactual (a wrong quote that is the right verse in another selected edition) is computed by `sacredbench facct` on a finished folder. It is not estimated here.",
        "",
        "## Cost",
        "",
        f"Input tokens {prompt:,}. Output tokens {completion:,}.",
    ]
    card = RUNS / model / "model.json"
    if card.exists():
        collected = json.loads(card.read_text(encoding="utf-8")).get("collected") or {}
        if collected.get("cost_usd") is not None:
            lines.append(f"Catalogue cost ${float(collected['cost_usd']):.4f}, from `model.json`.")
    if hosts:
        lines.append("Serving host: " + ", ".join(f"{name} {n}" for name, n in sorted(hosts.items())) + ".")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Write runs/<model>/analysis.md")
    parser.add_argument("--model", action="append", default=[])
    args = parser.parse_args()
    if args.model:
        models = args.model
    else:
        models = sorted({p.relative_to(RUNS).parts[0] for p in RUNS.glob("*/base/**/answers.jsonl")})
    if not models:
        raise SystemExit("no answer files under runs/")
    for model in models:
        dest = RUNS / model / "analysis.md"
        dest.write_text(report(model), encoding="utf-8")
        print(dest.relative_to(REPO))


if __name__ == "__main__":
    main()
