"""RQ3 figure: Jev form and claim-distance, by tradition.

Reads runs/*/base/**/jev_results/judgments-v5.jsonl. Coherent rows only enter the
bars. Incoherent rows are counted in the caption and left out of the stacks.
String-settled cells are absent from these files, so the figure is the residual
the string score did not settle.

Writes:
    runs/paper/judge-by-tradition.pdf
    .papers/judge-by-tradition.pdf
    .papers/judge-rq3.tex
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUNS = REPO / "runs"
OUT = REPO / "runs" / "paper"
PAPER = REPO / ".papers"

SKIP = {"paper", "archive"}
ORDER = (
    "Christianity",
    "Judaism",
    "Islam",
    "Hinduism",
    "Sikhism",
    "Buddhism",
    "Book of Mormon",
    "Encyclicals",
)
FOLDER = {
    "christianity": "Christianity",
    "judaism": "Judaism",
    "islam": "Islam",
    "hinduism": "Hinduism",
    "sikhism": "Sikhism",
    "buddhism": "Buddhism",
    "book-of-mormon": "Book of Mormon",
    "encyclicals": "Encyclicals",
}
KINDS = (
    ("refusal", "refusal", (0.45, 0.47, 0.50)),
    ("requested_wording", "requested words", (0.20, 0.50, 0.38)),
    ("faithful_paraphrase", "faithful paraphrase", (0.25, 0.45, 0.62)),
    ("meaning_change", "meaning change", (0.85, 0.62, 0.15)),
    ("wrong_passage", "wrong passage", (0.70, 0.28, 0.24)),
    ("neither", "neither", (0.55, 0.40, 0.62)),
)
THEOLOGY = (
    ("accurate", "accurate", (0.20, 0.50, 0.38)),
    ("gloss", "gloss", (0.25, 0.45, 0.62)),
    ("distorted", "distorted", (0.85, 0.62, 0.15)),
    ("contradicted", "contradicted", (0.70, 0.28, 0.24)),
)


def _pdf(page_w: int, page_h: int, commands: list[str]) -> bytes:
    stream = "\n".join(commands).encode("latin-1", "replace")
    objects: list[bytes] = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Count 1 /Kids [4 0 R] >>",
        b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
        (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {page_w} {page_h}] "
            "/Contents 3 0 R /Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> >>"
        ).encode(),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>",
    ]
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


def load() -> tuple[dict, dict, int, int]:
    kind: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    theology: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    rows = incoherent = 0
    for path in RUNS.glob("*/base/**/jev_results/judgments-v5.jsonl"):
        if SKIP.intersection(path.parts):
            continue
        parts = path.relative_to(RUNS).parts
        try:
            base = parts.index("base")
        except ValueError:
            continue
        tradition = FOLDER.get(parts[base + 1] if len(parts) > base + 1 else "")
        if tradition is None:
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            rows += 1
            if row.get("coherent") is False:
                incoherent += 1
                continue
            k = row.get("kind")
            if k in {name for name, _, _ in KINDS}:
                kind[tradition][k] += 1
            if k != "refusal" and row.get("theology") in {name for name, _, _ in THEOLOGY}:
                theology[tradition][row["theology"]] += 1
    return kind, theology, rows, incoherent


def _stack(commands: list[str], y: float, counts: dict[str, int], keys, bar_w: float, x0: float) -> int:
    total = sum(counts.get(k, 0) for k, _, _ in keys)
    x = x0
    if total:
        for key, _, color in keys:
            width = bar_w * counts.get(key, 0) / total
            if width:
                commands.append(
                    f"{x:.1f} {y - 2:.1f} {width:.1f} 12 re {color[0]:.2f} {color[1]:.2f} {color[2]:.2f} rg f"
                )
            x += width
    return total


def draw(kind, theology, rows: int, incoherent: int) -> bytes:
    page_w, page_h = 792, 460
    commands = [
        "0.98 0.98 0.97 rg 0 0 792 460 re f",
        "BT /F2 14 Tf 0.10 0.14 0.18 rg 28 428 Td (What the string score left unsettled) Tj ET",
        "BT /F1 8 Tf 0.33 0.36 0.40 rg 28 412 Td"
        " (Quote and completion the string match did not settle. Coherent Jev rows only. Shares within each tradition, not a ranking.) Tj ET",
        f"BT /F1 8 Tf 0.33 0.36 0.40 rg 28 400 Td"
        f" ({rows} judged, {incoherent} incoherent and omitted from the bars.) Tj ET",
        "BT /F2 10 Tf 0.12 0.14 0.18 rg 28 378 Td (Form of the answer) Tj ET",
        "BT /F2 10 Tf 0.12 0.14 0.18 rg 430 378 Td (Claim distance, when a passage was delivered) Tj ET",
    ]
    x = 250
    for _, label, color in KINDS:
        commands.append(f"{x:.0f} 362 8 8 re {color[0]:.2f} {color[1]:.2f} {color[2]:.2f} rg f")
        commands.append(f"BT /F1 7 Tf 0.20 0.22 0.24 rg {x + 11:.0f} 363 Td ({label}) Tj ET")
        x += 78
    y = 338
    for tradition in ORDER:
        total = _stack(commands, y, kind[tradition], KINDS, 250, 150)
        commands.append(f"BT /F1 8 Tf 0.12 0.14 0.16 rg 28 {y} Td ({tradition}) Tj ET")
        commands.append(f"BT /F1 7 Tf 0.33 0.36 0.40 rg 406 {y} Td (n={total}) Tj ET")
        claim = _stack(commands, y, theology[tradition], THEOLOGY, 180, 560)
        commands.append(f"BT /F1 7 Tf 0.33 0.36 0.40 rg 746 {y} Td (n={claim}) Tj ET")
        y -= 28
    commands.append("BT /F1 7 Tf 0.33 0.36 0.40 rg 430 362 Td (accurate, gloss, distorted, contradicted) Tj ET")
    commands.append(
        "BT /F1 7 Tf 0.33 0.36 0.40 rg 28 96 Td"
        " (Left: refusal, requested wording, faithful paraphrase, meaning change, wrong passage, neither.) Tj ET"
    )
    commands.append(
        "BT /F1 7 Tf 0.33 0.36 0.40 rg 28 84 Td"
        " (Right: among coherent delivered passages, accurate, gloss, distorted, contradicted. Spelling is not a distortion.) Tj ET"
    )
    commands.append(
        "BT /F1 7 Tf 0.33 0.36 0.40 rg 28 72 Td"
        " (A dropped clause is not accurate. These labels are descriptive until people label the same cells.) Tj ET"
    )
    return _pdf(page_w, page_h, commands)


def _pct(n: int, d: int) -> str:
    return "---" if not d else f"{100 * n / d:.1f}\\%"


def tex(kind, theology, rows: int, incoherent: int) -> str:
    lines = [
        "% Generated by items/for-test/jev_figure.py. Coherent sacredbench-jev-5 rows.",
        "\\begin{figure}[t]",
        "\\centering",
        "\\includegraphics[width=\\textwidth]{judge-by-tradition.pdf}",
        "\\caption{Form and claim-distance for quote and completion cells the string score did not settle. "
        f"Of {rows} judged rows, {incoherent} were incoherent and are omitted. "
        "Each bar is a share within that tradition. The right panel is restricted to coherent rows that delivered a passage.}",
        "\\label{fig:judge}",
        "\\end{figure}",
        "",
    ]
    coherent = rows - incoherent
    lines.append(
        f"On the cells the string score left open, Jev labeled {coherent} coherent rows "
        f"({_pct(coherent, rows)} of {rows} judged; {incoherent} incoherent rows are omitted). "
        "The split is not one harm scale. "
    )
    bits = []
    for tradition in ORDER[:6]:
        counts = kind[tradition]
        n = sum(counts.values())
        if not n:
            continue
        bits.append(
            f"{tradition}: refusal {_pct(counts['refusal'], n)}, "
            f"faithful paraphrase {_pct(counts['faithful_paraphrase'], n)}, "
            f"meaning change {_pct(counts['meaning_change'], n)}, "
            f"wrong passage {_pct(counts['wrong_passage'], n)} (n={n})"
        )
    lines.append("; ".join(bits) + ". ")
    claim_n = sum(sum(theology[t].values()) for t in ORDER[:6])
    distorted = sum(theology[t]["distorted"] + theology[t]["contradicted"] for t in ORDER[:6])
    lines.append(
        f"Among coherent delivered passages in the six traditions (n={claim_n}), "
        f"distorted or contradicted claims are {_pct(distorted, claim_n)}. "
        "Book of Mormon and encyclicals are drawn beside the six and are not pooled into them."
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    kind, theology, rows, incoherent = load()
    blob = draw(kind, theology, rows, incoherent)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "judge-by-tradition.pdf").write_bytes(blob)
    (PAPER / "judge-by-tradition.pdf").write_bytes(blob)
    (PAPER / "judge-rq3.tex").write_text(tex(kind, theology, rows, incoherent), encoding="utf-8")
    print(f"rows {rows} incoherent {incoherent}")
    for tradition in ORDER:
        print(tradition, dict(kind[tradition]), "claims", dict(theology[tradition]))


if __name__ == "__main__":
    main()
