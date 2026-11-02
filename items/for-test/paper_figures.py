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

TRADITIONS = (
    "Christianity", "Judaism", "Islam", "Hinduism", "Sikhism", "Buddhism",
    "Book of Mormon", "Encyclicals",
)
FOLDER_TRADITION = {"book-of-mormon": "Book of Mormon", "encyclicals": "Encyclicals"}


def _tradition_of(folder: str) -> str:
    return FOLDER_TRADITION.get(folder, folder.capitalize())
CONDITIONS = ("native-native", "english-native", "english-english")
CONDITION_LABEL = {"native-native": "NN", "english-native": "EN", "english-english": "EE"}
TASKS = ("retrieve_quote", "complete_unit", "cite_passage", "verify_source")
TEXT_TASKS = ("retrieve_quote", "complete_unit")
MINOR_F1 = 0.70
TASK_LABEL = {
    "retrieve_quote": "Retrieve",
    "complete_unit": "Complete",
    "cite_passage": "Cite",
    "verify_source": "Verify",
}


def _models() -> list[str]:
    panel = yaml.safe_load(PANEL.read_text(encoding="utf-8"))["models"]
    return [m["id"] for m in panel]


def _kind(posix: str) -> str | None:
    if "prompt-native" in posix:
        return "native-native"
    if "prompt-english" in posix:
        return "english-native"
    if "/english/" in posix:
        return "english-english"
    return None


def _expected_kind() -> dict[tuple[str, str], int]:
    counts: dict[tuple[str, str], int] = defaultdict(int)
    for path in RUNNABLE:
        tradition = _tradition_of(path.relative_to(ROOT).parts[0])
        kind = _kind(path.as_posix())
        if kind is None:
            continue
        counts[(tradition, kind)] += sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    return counts


def _expected() -> dict[tuple[str, str], int]:
    """Questions on disk for each model-agnostic (tradition, file) pair, keyed by tradition."""
    counts: dict[str, int] = defaultdict(int)
    files: dict[str, int] = defaultdict(int)
    for path in RUNNABLE:
        tradition = _tradition_of(path.relative_to(ROOT).parts[0])
        n = sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
        counts[tradition] += n
        files[tradition] += 1
    return counts


def _collect(models: list[str]) -> tuple[dict, dict]:
    """Return (tradition cells, task cells). Each cell is correct, incorrect, refused."""
    by_trad = {(m, t): {"correct": 0, "incorrect": 0, "refused": 0, "n": 0} for m in models for t in TRADITIONS}
    by_kind = {
        (m, t, k): {"correct": 0, "incorrect": 0, "refused": 0, "n": 0}
        for m in models for t in TRADITIONS for k in CONDITIONS
    }
    by_task = {
        (m, tradition, t): {"correct": 0, "incorrect": 0, "refused": 0, "n": 0}
        for m in models for tradition in TRADITIONS for t in TASKS
    }
    by_grade = {
        (m, tradition, t): {"correct": 0, "minor": 0, "major": 0, "refused": 0, "f1": 0.0, "f1n": 0, "n": 0}
        for m in models for tradition in TRADITIONS for t in TEXT_TASKS
    }
    seen = {(m, t): 0 for m in models for t in TRADITIONS}
    for model in models:
        base = RUNS / model / "base"
        if not base.is_dir():
            continue
        for path in base.rglob("answers.jsonl"):
            folder = path.relative_to(base).parts[0]
            tradition = _tradition_of(folder)
            if tradition not in TRADITIONS:
                continue
            seen[(model, tradition)] += 1
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                row = json.loads(line)
                question = row.get("question") or {}
                task = row.get("task") or ""
                language = (question.get("source") or {}).get("language")
                metrics = score_answer(task, row.get("answer") or "", question.get("expected") or {}, language=language)
                outcome = metrics.get("outcome") or "incorrect"
                by_trad[(model, tradition)][outcome] += 1
                by_trad[(model, tradition)]["n"] += 1
                kind = _kind(path.as_posix())
                if kind is not None:
                    by_kind[(model, tradition, kind)][outcome] += 1
                    by_kind[(model, tradition, kind)]["n"] += 1
                if task in TASKS:
                    cell = by_task[(model, tradition, task)]
                    cell[outcome] += 1
                    cell["n"] += 1
                if task in TEXT_TASKS:
                    grade = by_grade[(model, tradition, task)]
                    grade["n"] += 1
                    f1 = metrics.get("token_f1")
                    if outcome == "correct":
                        grade["correct"] += 1
                    elif outcome == "refused":
                        grade["refused"] += 1
                    elif f1 is not None and float(f1) >= MINOR_F1:
                        grade["minor"] += 1
                    else:
                        grade["major"] += 1
                    if f1 is not None and outcome != "refused":
                        grade["f1"] += float(f1)
                        grade["f1n"] += 1
    return by_trad, by_task, by_kind, by_grade


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
        cells = " & ".join(_cell_tex(by_trad[(model, t)], expected[t]) for t in TRADITIONS)
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
        if not any(by_task[(model, tradition, t)]["n"] for tradition in TRADITIONS for t in TASKS):
            continue
        cells = []
        for task in TASKS:
            correct = sum(by_task[(model, tradition, task)]["correct"] for tradition in TRADITIONS)
            incorrect = sum(by_task[(model, tradition, task)]["incorrect"] for tradition in TRADITIONS)
            answered = correct + incorrect
            cells.append("---" if not answered else f"{100 * correct / answered:.1f}")
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
    page_w, page_h = 1180, 700
    left, row_h, col_w = 130, 32, 125
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
            star = "*" if cell["n"] < expected[tradition] else ""
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


def _pdf_conditions(models: list[str], by_kind: dict, expected: dict[tuple[str, str], int]) -> bytes:
    """Models by tradition, each tradition split into NN, EN, and EE."""
    page_w, page_h = 1280, 720
    left, row_h, col_w = 120, 32, 46
    group = col_w * 3
    grid_top = page_h - 118
    commands = [
        "0.98 0.98 0.97 rg",
        f"0 0 {page_w} {page_h} re f",
        "BT /F2 16 Tf 0.10 0.14 0.18 rg 36 684 Td (Accuracy by tradition and prompt) Tj ET",
        "BT /F1 9 Tf 0.33 0.36 0.40 rg 36 666 Td"
        " (NN native prompt, native text. EN English prompt, native text. EE English prompt, English text.) Tj ET",
        "BT /F1 9 Tf 0.33 0.36 0.40 rg 36 652 Td"
        " (Percent correct among answers that were not refusals. Empty is not run. A star is unfinished.) Tj ET",
    ]
    for i, tradition in enumerate(TRADITIONS):
        x = left + i * group
        commands.append(f"BT /F2 8 Tf 0.15 0.18 0.22 rg {x + 18} {grid_top + 22} Td ({tradition}) Tj ET")
        for j, kind in enumerate(CONDITIONS):
            label = CONDITION_LABEL[kind]
            commands.append(
                f"BT /F1 7 Tf 0.35 0.38 0.42 rg {x + j * col_w + 12} {grid_top + 8} Td ({label}) Tj ET"
            )
    for r, model in enumerate(models):
        y = grid_top - (r + 1) * row_h
        commands.append(f"BT /F1 8 Tf 0.12 0.14 0.16 rg 28 {y + 11} Td ({model}) Tj ET")
        for i, tradition in enumerate(TRADITIONS):
            for j, kind in enumerate(CONDITIONS):
                x = left + i * group + j * col_w
                cell = by_kind[(model, tradition, kind)]
                acc = _accuracy(cell)
                commands.append(f"{x} {y} {col_w - 3} {row_h - 4} re")
                need = expected.get((tradition, kind), 0)
                if acc is None or need == 0:
                    commands.append("0.93 0.93 0.91 rg f")
                    continue
                red, green, blue = _fill(acc)
                commands.append(f"{red:.3f} {green:.3f} {blue:.3f} rg f")
                ink = "1 1 1" if acc >= 0.62 else "0.10 0.14 0.20"
                star = "*" if cell["n"] < need else ""
                label = f"{100 * acc:.0f}{star}"
                commands.append(f"BT /F2 8 Tf {ink} rg {x + 8} {y + 10} Td ({label}) Tj ET")
    legend_y = 28
    commands.append("BT /F1 8 Tf 0.33 0.36 0.40 rg 36 46 Td (0) Tj ET")
    for step in range(11):
        acc = step / 10
        red, green, blue = _fill(acc)
        x = 52 + step * 22
        commands.append(f"{x} {legend_y} 22 10 re {red:.3f} {green:.3f} {blue:.3f} rg f")
    commands.append("BT /F1 8 Tf 0.33 0.36 0.40 rg 300 46 Td (100 percent correct) Tj ET")
    stream = "\n".join(commands).encode("latin-1")
    objects = []

    def add(body: bytes) -> None:
        objects.append(body)

    add(b"<< /Type /Catalog /Pages 2 0 R >>")
    add(b"<< /Type /Pages /Count 1 /Kids [3 0 R] >>")
    add(
        f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {page_w} {page_h}] "
        f"/Contents 4 0 R /Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> >>".encode()
    )
    add(b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream")
    add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{index} 0 obj\n".encode() + body + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for offset in offsets[1:]:
        out += f"{offset:010d} 00000 n \n".encode()
    out += f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    return bytes(out)


def _pdf_bytes(page_w: int, page_h: int, commands: list[str] | list[list[str]]) -> bytes:
    pages = commands if commands and isinstance(commands[0], list) else [commands]
    # objects: catalog, pages, then each page + its content, then two fonts
    kids = []
    objects: list[bytes] = [b"", b""]
    font_helv = len(pages) * 2 + 3
    font_bold = font_helv + 1
    for index, page in enumerate(pages):
        content_id = 3 + index * 2
        page_id = content_id + 1
        kids.append(f"{page_id} 0 R")
        stream = "\n".join(page).encode("latin-1", "replace")
        objects.append(b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream")
        objects.append(
            (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {page_w} {page_h}] "
                f"/Contents {content_id} 0 R /Resources << /Font << /F1 {font_helv} 0 R /F2 {font_bold} 0 R >> >> >>"
            ).encode()
        )
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    objects[0] = b"<< /Type /Catalog /Pages 2 0 R >>"
    objects[1] = f"<< /Type /Pages /Count {len(pages)} /Kids [{' '.join(kids)}] >>".encode()
    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{index} 0 obj\n".encode() + body + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for offset in offsets[1:]:
        out += f"{offset:010d} 00000 n \n".encode()
    out += f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    return bytes(out)


def _active(models: list[str], by_task: dict) -> list[str]:
    return [
        model for model in models
        if any(by_task[(model, tradition, task)]["n"] for tradition in TRADITIONS for task in TASKS)
    ]


def _rates(cell: dict) -> tuple[float | None, float | None, float | None]:
    n = cell["n"]
    if not n:
        return None, None, None
    answered = cell["correct"] + cell["incorrect"]
    accuracy = None if not answered else cell["correct"] / answered
    coverage = answered / n
    refusal = cell["refused"] / n
    return accuracy, coverage, refusal


def _pdf_tasks(models: list[str], by_task: dict, expected: dict[str, int]) -> bytes:
    """Four tasks by tradition: accuracy, coverage, and refusal rate. One page per model."""
    active = _active(models, by_task)
    page_w, page_h = 980, 520
    pages = []
    left, group = 130, 200
    for model in active:
        commands = [
            "0.98 0.98 0.97 rg",
            f"0 0 {page_w} {page_h} re f",
            f"BT /F2 16 Tf 0.10 0.14 0.18 rg 28 {page_h - 36} Td ({model}: four tasks by tradition) Tj ET",
            f"BT /F1 9 Tf 0.33 0.36 0.40 rg 28 {page_h - 54} Td"
            " (Each cell is accuracy, coverage, refusal, in percent. Accuracy excludes refusals. A star is unfinished.) Tj ET",
        ]
        y = page_h - 86
        commands.append(f"BT /F2 11 Tf 0.12 0.14 0.18 rg 28 {y} Td ({model}) Tj ET")
        y -= 16
        for i, task in enumerate(TASKS):
            x = left + i * group
            commands.append(f"BT /F2 8 Tf 0.15 0.18 0.22 rg {x} {y} Td ({TASK_LABEL[task]}) Tj ET")
            commands.append(f"BT /F1 7 Tf 0.40 0.42 0.45 rg {x} {y - 11} Td (acc  cov  ref) Tj ET")
        y -= 24
        for tradition in TRADITIONS:
            commands.append(f"BT /F1 8 Tf 0.12 0.14 0.16 rg 28 {y} Td ({tradition}) Tj ET")
            need = expected.get(tradition, 0) // len(TASKS)
            for i, task in enumerate(TASKS):
                cell = by_task[(model, tradition, task)]
                accuracy, coverage, refusal = _rates(cell)
                x = left + i * group
                if accuracy is None:
                    commands.append(f"BT /F1 8 Tf 0.55 0.55 0.52 rg {x} {y} Td (---) Tj ET")
                    continue
                red, green, blue = _fill(accuracy)
                commands.append(f"{x - 2} {y - 3} 36 14 re {red:.3f} {green:.3f} {blue:.3f} rg f")
                ink = "1 1 1" if accuracy >= 0.62 else "0.10 0.14 0.20"
                star = "*" if cell["n"] < need else ""
                commands.append(f"BT /F2 8 Tf {ink} rg {x} {y} Td ({100 * accuracy:.0f}{star}) Tj ET")
                commands.append(
                    f"BT /F1 8 Tf 0.20 0.24 0.28 rg {x + 42} {y} Td ({100 * coverage:.0f}   {100 * refusal:.0f}) Tj ET"
                )
            y -= 22
        pages.append(commands)
    return _pdf_bytes(page_w, page_h, pages)


def _pdf_errors(models: list[str], by_grade: dict) -> bytes:
    """Major and minor misses on retrieve and complete. One page per model."""
    active = [
        model for model in models
        if any(by_grade[(model, tradition, task)]["n"] for tradition in TRADITIONS for task in TEXT_TASKS)
    ]
    page_w, page_h = 980, 560
    pages = []
    bar_w = 300
    for model in active:
        commands = [
            "0.98 0.98 0.97 rg",
            f"0 0 {page_w} {page_h} re f",
            f"BT /F2 16 Tf 0.10 0.14 0.18 rg 28 {page_h - 32} Td ({model}: major and minor misses) Tj ET",
            f"BT /F1 9 Tf 0.33 0.36 0.40 rg 28 {page_h - 50} Td"
            " (Quote and completion. Minor is incorrect with token F1 at least 0.70. The bar includes refusals.) Tj ET",
            f"BT /F1 8 Tf 0.20 0.50 0.35 rg 280 {page_h - 70} Td (correct) Tj ET",
            f"BT /F1 8 Tf 0.75 0.55 0.15 rg 360 {page_h - 70} Td (minor) Tj ET",
            f"BT /F1 8 Tf 0.65 0.25 0.22 rg 430 {page_h - 70} Td (major) Tj ET",
            f"BT /F1 8 Tf 0.45 0.47 0.50 rg 500 {page_h - 70} Td (refused) Tj ET",
        ]
        y = page_h - 96
        commands.append(f"BT /F2 11 Tf 0.12 0.14 0.18 rg 28 {y} Td ({model}) Tj ET")
        y -= 18
        for tradition in TRADITIONS:
            for task in TEXT_TASKS:
                grade = by_grade[(model, tradition, task)]
                total = grade["n"]
                if not total:
                    continue
                mean = "n/a" if not grade["f1n"] else f"{grade['f1'] / grade['f1n']:.2f}"
                refusal = 100 * grade["refused"] / total
                commands.append(
                    f"BT /F1 7 Tf 0.12 0.14 0.16 rg 28 {y} Td"
                    f" ({tradition} {TASK_LABEL[task]}  F1 {mean}  ref {refusal:.0f}%) Tj ET"
                )
                x = 280
                for key, color in (
                    ("correct", (0.20, 0.50, 0.38)),
                    ("minor", (0.85, 0.62, 0.15)),
                    ("major", (0.70, 0.28, 0.24)),
                    ("refused", (0.72, 0.74, 0.76)),
                ):
                    width = bar_w * grade[key] / total
                    if width:
                        commands.append(
                            f"{x:.1f} {y - 2:.1f} {width:.1f} 11 re {color[0]:.2f} {color[1]:.2f} {color[2]:.2f} rg f"
                        )
                    x += width
                commands.append(
                    f"BT /F1 7 Tf 0.25 0.28 0.30 rg {280 + bar_w + 8:.0f} {y} Td"
                    f" ({grade['correct']} / {grade['minor']} / {grade['major']} / {grade['refused']}) Tj ET"
                )
                y -= 16
        pages.append(commands)
    return _pdf_bytes(page_w, page_h, pages)


def write_early() -> None:
    """Roll up finished summary.json files. A partial file is not included."""
    from collections import defaultdict

    bucket: dict = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [0, 0, 0])))
    for path in (RUNS).glob("*/base/**/summary.json"):
        rel = path.relative_to(RUNS)
        model = rel.parts[0]
        tradition = rel.parts[2]
        summary = json.loads(path.read_text(encoding="utf-8"))
        block = (summary.get("models") or {}).get(model) or {}
        for task, cell in block.items():
            if not isinstance(cell, dict) or task.startswith("_"):
                continue
            slot = bucket[model][tradition][task]
            slot[0] += int(cell.get("correct") or 0)
            slot[1] += int(cell.get("incorrect") or 0)
            slot[2] += int(cell.get("refused") or 0)
    lines = [
        "# Early outcomes",
        "",
        "Finished population files only, from each folder's `summary.json`. "
        "Accuracy is correct / (correct + incorrect). Coverage is (correct + incorrect) / n. "
        "A tradition still being collected is omitted.",
        "",
        "| model | tradition | task | n | accuracy | coverage | refused |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for model in sorted(bucket):
        for tradition in TRADITIONS:
            key = tradition.lower()
            tasks = bucket[model].get(key)
            if not tasks:
                continue
            for task in TASKS:
                if task not in tasks:
                    continue
                correct, incorrect, refused = tasks[task]
                n = correct + incorrect + refused
                answered = correct + incorrect
                accuracy = "—" if not answered else f"{100 * correct / answered:.1f}%"
                coverage = "—" if not n else f"{100 * answered / n:.1f}%"
                lines.append(
                    f"| {model} | {tradition} | {task} | {n} | {accuracy} | {coverage} | {refused} |"
                )
    lines.append("")
    (OUT / "early-outcomes.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    models = _models()
    expected = _expected()
    by_trad, by_task, by_kind, by_grade = _collect(models)
    write_tex(models, by_trad, by_task, expected)
    (OUT / "models-by-tradition.pdf").write_bytes(_pdf(models, by_trad, expected))
    (OUT / "models-by-condition.pdf").write_bytes(_pdf_conditions(models, by_kind, _expected_kind()))
    print(OUT.relative_to(REPO) / "models-by-condition.pdf")
    (OUT / "models-by-task.pdf").write_bytes(_pdf_tasks(models, by_task, expected))
    (OUT / "models-by-error.pdf").write_bytes(_pdf_errors(models, by_grade))
    print(OUT.relative_to(REPO) / "models-by-task.pdf")
    print(OUT.relative_to(REPO) / "models-by-error.pdf")
    print(OUT.relative_to(REPO) / "models-by-tradition.pdf")
    print(OUT.relative_to(REPO) / "models-by-tradition.tex")
    print(OUT.relative_to(REPO) / "models-by-task.tex")
    write_early()
    print(OUT.relative_to(REPO) / "early-outcomes.md")


if __name__ == "__main__":
    main()
