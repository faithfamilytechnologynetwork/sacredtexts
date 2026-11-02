"""Paper figure and LaTeX tables: accuracy by model and tradition.

Scores whatever answers are on disk. A tradition with no answers is a dash.
A tradition that has been started and not finished is marked partial. Writes:

    runs/paper/models-by-tradition.pdf
    runs/paper/models-by-tradition.tex
    runs/paper/models-by-task.tex

    python3 items/for-test/paper_figures.py
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
RUNS = REPO / "runs"
OUT = RUNS / "paper"
sys.path.insert(0, str(REPO / "pipelines"))

from cost import PANEL, RUNNABLE  # noqa: E402
from sacredbench.score import score_answer  # noqa: E402

TRADITIONS = ("Christianity", "Judaism", "Islam", "Hinduism", "Sikhism", "Buddhism")
TASKS = ("retrieve_quote", "complete_unit", "cite_passage", "verify_source")


def _models() -> list[str]:
    panel = yaml.safe_load(PANEL.read_text(encoding="utf-8"))["models"]
    return [m["id"] for m in panel]


def _expected() -> dict[tuple[str, str], int]:
    """Questions on disk for each model-agnostic (tradition, file) pair, keyed by tradition."""
    counts: dict[str, int] = defaultdict(int)
    files: dict[str, int] = defaultdict(int)
    for path in RUNNABLE:
        tradition = path.relative_to(ROOT).parts[0]
        n = sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
        counts[tradition] += n
        files[tradition] += 1
    return counts


def _collect(models: list[str]) -> tuple[dict, dict]:
    """Return (tradition cells, task cells). Each cell is correct, incorrect, refused."""
    by_trad = {(m, t): {"correct": 0, "incorrect": 0, "refused": 0, "n": 0} for m in models for t in TRADITIONS}
    by_task = {(m, t): {"correct": 0, "incorrect": 0, "refused": 0} for m in models for t in TASKS}
    seen = {(m, t): 0 for m in models for t in TRADITIONS}
    for model in models:
        base = RUNS / model / "base"
        if not base.is_dir():
            continue
        for path in base.rglob("answers.jsonl"):
            tradition = path.relative_to(base).parts[0].capitalize()
            if tradition not in TRADITIONS:
                continue
            seen[(model, tradition)] += 1
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                row = json.loads(line)
                question = row.get("question") or {}
                task = row.get("task") or ""
                metrics = score_answer(task, row.get("answer") or "", question.get("expected") or {})
                outcome = metrics.get("outcome") or "incorrect"
                by_trad[(model, tradition)][outcome] += 1
                by_trad[(model, tradition)]["n"] += 1
                if task in TASKS:
                    by_task[(model, task)][outcome] += 1
    return by_trad, by_task


def _accuracy(cell: dict) -> float | None:
    answered = cell["correct"] + cell["incorrect"]
    if cell["n"] == 0 or answered == 0:
        return None
    return cell["correct"] / answered


def _tex_escape(text: str) -> str:
    return text.replace("_", r"\_")


def _cell_tex(cell: dict, expected: int) -> str:
    acc = _accuracy(cell)
    if acc is None:
        return "---"
    mark = r"$^{\ast}$" if cell["n"] < expected else ""
    return f"{100 * acc:.1f}{mark}"


def write_tex(models: list[str], by_trad: dict, by_task: dict, expected: dict[str, int]) -> None:
    header = " & ".join(rf"\textbf{{{t}}}" for t in TRADITIONS)
    rows = []
    for model in models:
        cells = " & ".join(_cell_tex(by_trad[(model, t)], expected[t.lower()]) for t in TRADITIONS)
        rows.append(f"{_tex_escape(model)} & {cells} \\\\")
    body = "\n".join(rows)
    cols = "l" + "r" * len(TRADITIONS)
    (OUT / "models-by-tradition.tex").write_text(
        "\n".join([
            "% Accuracy, percent. A dash has not been run. An asterisk is a partial tradition.",
            "\\begin{table}[t]",
            "\\centering",
            "\\caption{Accuracy by tradition. Accuracy is correct divided by correct plus incorrect. "
            "Refusals are excluded. Search off, temperature 0.}",
            "\\label{tab:accuracy-tradition}",
            f"\\begin{{tabular}}{{{cols}}}",
            "\\toprule",
            f"\\textbf{{Model}} & {header} \\\\",
            "\\midrule",
            body,
            "\\bottomrule",
            "\\end{tabular}",
            "\\end{table}",
            "",
        ]),
        encoding="utf-8",
    )
    task_header = " & ".join(rf"\textbf{{{_tex_escape(t)}}}" for t in TASKS)
    task_rows = []
    for model in models:
        if not any(by_task[(model, t)]["correct"] + by_task[(model, t)]["incorrect"] + by_task[(model, t)]["refused"] for t in TASKS):
            continue
        cells = []
        for task in TASKS:
            cell = by_task[(model, task)]
            answered = cell["correct"] + cell["incorrect"]
            cells.append("---" if not answered else f"{100 * cell['correct'] / answered:.1f}")
        task_rows.append(f"{_tex_escape(model)} & " + " & ".join(cells) + " \\\\")
    if not task_rows:
        task_rows.append("% no scored model yet")
    (OUT / "models-by-task.tex").write_text(
        "\n".join([
            "% Accuracy by task, percent, across every tradition scored so far.",
            "\\begin{table}[t]",
            "\\centering",
            "\\caption{Accuracy by task, on the answers collected so far. "
            "A model with an unfinished tradition is not a finished result.}",
            "\\label{tab:accuracy-task}",
            "\\begin{tabular}{lrrrr}",
            "\\toprule",
            f"\\textbf{{Model}} & {task_header} \\\\",
            "\\midrule",
            "\n".join(task_rows),
            "\\bottomrule",
            "\\end{tabular}",
            "\\end{table}",
            "",
        ]),
        encoding="utf-8",
    )


def _fill(acc: float) -> tuple[float, float, float]:
    """Pale blue at 0, deep blue at 1. One hue, so a printout still reads."""
    return (0.93 - 0.78 * acc, 0.95 - 0.62 * acc, 0.98 - 0.40 * acc)


def _pdf(models: list[str], by_trad: dict, expected: dict[str, int]) -> bytes:
    """One landscape page. Pending cells are empty. Partial cells carry a star."""
    page_w, page_h = 792, 700
    left, row_h, col_w = 150, 32, 100
    grid_top = page_h - 92
    commands = [
        "0.98 0.98 0.97 rg",
        f"0 0 {page_w} {page_h} re f",
        "BT /F2 18 Tf 0.10 0.14 0.18 rg 36 662 Td (Accuracy by tradition) Tj ET",
        "BT /F1 9 Tf 0.33 0.36 0.40 rg 36 644 Td"
        " (Correct divided by correct plus incorrect. Empty is not run. A star is unfinished.) Tj ET",
    ]
    for i, tradition in enumerate(TRADITIONS):
        x = left + i * col_w
        commands.append(f"BT /F2 8 Tf 0.15 0.18 0.22 rg {x + 14} {grid_top + 8} Td ({tradition}) Tj ET")
    for r, model in enumerate(models):
        y = grid_top - (r + 1) * row_h
        commands.append(f"BT /F1 8 Tf 0.12 0.14 0.16 rg 36 {y + 12} Td ({model}) Tj ET")
        for c, tradition in enumerate(TRADITIONS):
            x = left + c * col_w
            cell = by_trad[(model, tradition)]
            acc = _accuracy(cell)
            commands.append(f"{x} {y} {col_w - 4} {row_h - 4} re")
            if acc is None:
                commands.append("0.93 0.93 0.91 rg f")
                commands.append(f"0.6 w 0.86 0.86 0.84 RG {x} {y} {col_w - 4} {row_h - 4} re S")
                continue
            red, green, blue = _fill(acc)
            commands.append(f"{red:.3f} {green:.3f} {blue:.3f} rg f")
            ink = "1 1 1" if acc >= 0.62 else "0.10 0.14 0.20"
            star = "*" if cell["n"] < expected[tradition.lower()] else ""
            label = f"{100 * acc:.0f}{star}"
            commands.append(f"BT /F2 10 Tf {ink} rg {x + 36} {y + 10} Td ({label}) Tj ET")
    legend_y = 36
    commands.append("BT /F1 8 Tf 0.33 0.36 0.40 rg 36 58 Td (0) Tj ET")
    for i in range(11):
        acc = i / 10
        red, green, blue = _fill(acc)
        x = 52 + i * 28
        commands.append(f"{x} {legend_y} 28 12 re {red:.3f} {green:.3f} {blue:.3f} rg f")
    commands.append("BT /F1 8 Tf 0.33 0.36 0.40 rg 366 58 Td (100) Tj ET")
    commands.append("BT /F1 8 Tf 0.33 0.36 0.40 rg 420 46 Td (percent correct) Tj ET")
    stream = "\n".join(commands).encode("latin-1")
    objects = []

    def add(body: bytes) -> int:
        objects.append(body)
        return len(objects)

    add(b"<< /Type /Catalog /Pages 2 0 R >>")
    add(
        f"<< /Type /Pages /Count 1 /Kids [3 0 R] >>".encode()
    )
    add(
        f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {page_w} {page_h}] "
        f"/Contents 4 0 R /Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> >>".encode()
    )
    add(b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream")
    add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for i, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode() + body + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for offset in offsets[1:]:
        out += f"{offset:010d} 00000 n \n".encode()
    out += f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    return bytes(out)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    models = _models()
    expected = _expected()
    by_trad, by_task = _collect(models)
    write_tex(models, by_trad, by_task, expected)
    (OUT / "models-by-tradition.pdf").write_bytes(_pdf(models, by_trad, expected))
    print(OUT.relative_to(REPO) / "models-by-tradition.pdf")
    print(OUT.relative_to(REPO) / "models-by-tradition.tex")
    print(OUT.relative_to(REPO) / "models-by-task.tex")


if __name__ == "__main__":
    main()
