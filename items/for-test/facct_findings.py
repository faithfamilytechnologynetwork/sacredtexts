"""Two findings that a single accuracy number hides.

Reads finished ``scores.jsonl`` files under one run dir, joined to the saved answers. Writes
``runs/paper/findings.md`` and ``runs/paper/takeaway.pdf``. Stops when an answer row in the
run dir has no population question, unless --allow-partial.

    uv --project pipelines run python items/for-test/facct_findings.py --run-dir runs/rerun-2026-11-03
"""

from __future__ import annotations

import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Annotated

import typer
from paper_join import REPO, check_coverage, model_files, partial_note, population_questions, resolve_run_dir
from paper_join import rows as _rows

ROOT = REPO
OUT = ROOT / "runs" / "paper" / "findings.md"


def _answers(run_dir: Path) -> dict[tuple[str, str], dict]:
    return {
        (model, row["question_id"]): row
        for model, path in model_files(run_dir, "answers.jsonl")
        for row in _rows(path)
    }


def _load(run_dir: Path) -> list[dict]:
    answers = _answers(run_dir)
    joined = []
    for model, path in model_files(run_dir, "scores.jsonl"):
        folder = "/".join(path.relative_to(run_dir).parts[2:-1])
        for score in _rows(path):
            answer = answers.get((model, score["question_id"]))
            if not answer:
                continue
            question = answer.get("question") or {}
            expected = question.get("expected") or {}
            metrics = score.get("metrics") or {}
            joined.append(
                {
                    "model": model,
                    "folder": folder,
                    "question_id": score.get("question_id"),
                    "task": score.get("task"),
                    "outcome": metrics.get("outcome"),
                    "f1": metrics.get("token_f1"),
                    "expected_yn": expected.get("answer"),
                }
            )
    return joined


_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")


def _fold_cite(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    text = text.translate(_DIGITS)
    return re.sub(r"\s+", " ", text).strip().lower()


def _pct(ok: int, n: int) -> str:
    if not n:
        return "—"
    return f"{100 * ok / n:.0f}%"


def _tally(rows: list[dict]) -> tuple[int, int, int]:
    correct = sum(r["outcome"] == "correct" for r in rows)
    refused = sum(r["outcome"] == "refused" for r in rows)
    return correct, len(rows) - correct - refused, refused


def _verify(rows: list[dict]) -> list[str]:
    lines = [
        "## Models believe a fake more easily than the real text",
        "",
        "On verify, a correct `no` means the model rejected a passage that is not from the named edition. "
        "A correct `yes` means it recognized a passage that is. Refusals are counted separately.",
        "",
        "| model | real text (`yes`) | not from the edition (`no`) |",
        "|---|---:|---:|",
    ]
    models = sorted({r["model"] for r in rows if r["task"] == "verify_source"})
    for model in models:
        cells = []
        for kind in ("yes", "no"):
            subset = [r for r in rows if r["model"] == model and r["task"] == "verify_source" and r["expected_yn"] == kind]
            correct, _incorrect, refused = _tally(subset)
            answered = len(subset) - refused
            cells.append(f"{_pct(correct, answered)} of {answered}, refused {refused}")
        lines.append(f"| {model} | {cells[0]} | {cells[1]} |")
    lines += [
        "",
        "A model that is sure about fakes and unsure about the real text will look accurate on a set that is half `no`. "
        "That accuracy is not recognition.",
        "",
    ]
    return lines


def _negative_kind(question: dict) -> str:
    import sys
    sys.path.insert(0, str(ROOT / "pipelines"))
    from sacredbench.claims import negative_kind

    src = question["source"]
    asked = src["tradition"][0] if isinstance(src.get("tradition"), list) else src.get("tradition")
    true = (question.get("expected") or {}).get("true_tradition")
    return negative_kind(src.get("language"), asked, true)


def _instrument(rows: list[dict], questions: dict[str, dict]) -> list[str]:
    tally: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0])
    for row in rows:
        if row["task"] != "verify_source" or row["expected_yn"] != "no":
            continue
        question = questions.get(row["question_id"])
        if not question:
            continue
        slot = tally[_negative_kind(question)]
        if row["outcome"] == "correct":
            slot[0] += 1
        elif row["outcome"] == "incorrect":
            slot[1] += 1
        elif row["outcome"] == "refused":
            slot[2] += 1
    order = [
        "Different script",
        "NRSV shown the Book of Mormon",
        "Qur'an shown a hadith",
        "Encyclical shown the Book of Mormon",
        "Other same-script negative",
        "Talmud shown the Bible",
        "Book of Mormon shown an encyclical",
    ]
    lines = [
        "## The negative item is an alphabet check for some traditions",
        "",
        "A correct `no` is not the same question in every file. Sikhism, the Sanskrit Gita, "
        "the Pali Dhammapada, and the Greek New Testament are shown a passage in another script, "
        "because this corpus has no second work in Gurmukhi, Devanagari, Pali, or Greek. "
        "Islam is shown a hadith. The Talmud is shown the Bible. The Book of Mormon is shown a "
        "papal encyclical, and the encyclical is shown the Book of Mormon. Refusals are out of the percent.",
        "",
        "| negative the model was shown | correct no | wrong yes | refused |",
        "|---|---:|---:|---:|",
    ]
    for name in order:
        correct, incorrect, refused = tally.get(name, [0, 0, 0])
        answered = correct + incorrect
        if not answered and not refused:
            continue
        lines.append(
            f"| {name} | {_pct(correct, answered)} ({correct}/{answered}) | {incorrect} | {refused} |"
        )
    lines += [
        "",
        "Saying no to a different alphabet is nearly automatic. Saying no to the Bible when the "
        "question names the Talmud, and saying no to an encyclical when the question names the "
        "Book of Mormon, is where the errors are. The reverse pair is not the same: shown a Book "
        "of Mormon verse and asked if it is the encyclical, models almost always say no. "
        "A verify accuracy that averages these items ranks a tradition by how its negative was built.",
        "",
    ]
    return lines


def _dissociation(rows: list[dict]) -> list[str]:
    lines = [
        "## Quoting and citing are different skills",
        "",
        "Each finished file, retrieve against cite. A wide gap means the model can do one and not the other. "
        "Refusals are out of the percent and shown beside it.",
        "",
        "| model | file | retrieve | cite |",
        "|---|---|---:|---:|",
    ]
    files = sorted({(r["model"], r["folder"]) for r in rows})
    gaps = []
    for model, folder in files:
        pair = []
        for task in ("retrieve_quote", "cite_passage"):
            subset = [r for r in rows if r["model"] == model and r["folder"] == folder and r["task"] == task]
            if not subset:
                pair.append(None)
                continue
            correct, _incorrect, refused = _tally(subset)
            answered = len(subset) - refused
            pair.append((correct, answered, refused))
        if not pair[0] or not pair[1] or not pair[0][1] or not pair[1][1]:
            continue
        retrieve = 100 * pair[0][0] / pair[0][1]
        cite = 100 * pair[1][0] / pair[1][1]
        gaps.append((abs(retrieve - cite), model, folder, retrieve, cite, pair))
    for _gap, model, folder, retrieve, cite, pair in sorted(gaps, reverse=True):
        def cell(item, rate):
            correct, answered, refused = item
            return f"{rate:.0f}% ({correct}/{answered}, refused {refused})"
        lines.append(f"| {model} | `{folder}` | {cell(pair[0], retrieve)} | {cell(pair[1], cite)} |")
    lines += [
        "",
        "The flip is inside one model, on the same verses. "
        "Gemini Flash, Qur'an prompted in Arabic: quotation 28/30 and citation 30/30. "
        "The same file prompted in English: quotation 28/30 and citation 1/30. "
        "Hebrew Masoretic text prompted in Hebrew: citation 21/21, quotation 0/21. "
        "Prompted in English: citation 0/21 and quotation 0/21. "
        "Greek prompted in English: quotation 8/9, citation 0/9. "
        "Naming the verse and producing its words come apart, and the prompt language decides which one is available.",
        "",
    ]
    return lines


def _near(rows: list[dict]) -> list[str]:
    near = [r for r in rows if r["outcome"] == "incorrect" and r["f1"] is not None and r["f1"] >= 0.7]
    by = defaultdict(int)
    for row in near:
        by[(row["model"], row["task"])] += 1
    lines = [
        "## Close wording that still scores incorrect",
        "",
        f"{len(near)} incorrect answers still have token F1 of at least 0.70. "
        "The strict score is doing what it was built for: a near miss is not a hit. "
        "Most of them are Gemini Flash completions.",
        "",
    ]
    for (model, task), n in sorted(by.items(), key=lambda item: -item[1]):
        lines.append(f"- {model}, {task}: {n}")
    lines.append("")
    return lines


def _digits(run_dir: Path) -> list[str]:
    """Wrong cites that are the right citation once Arabic digits are folded."""
    # Re-read answers; the joined rows do not carry the raw answer.
    answers = _answers(run_dir)
    rescued = defaultdict(int)
    still = 0
    samples = []
    for model, path in model_files(run_dir, "scores.jsonl"):
        for score in _rows(path):
            if score.get("task") != "cite_passage":
                continue
            if (score.get("metrics") or {}).get("outcome") != "incorrect":
                continue
            answer = answers.get((model, score["question_id"]))
            if not answer:
                continue
            gold = ((answer.get("question") or {}).get("expected") or {}).get("citation") or ""
            got = (answer.get("answer") or "").strip().split("\n")[0]
            folded = _fold_cite(got)
            if folded == _fold_cite(gold) or _fold_cite(gold) in folded:
                rescued[model] += 1
                if len(samples) < 3:
                    samples.append((model, gold, got.strip()))
            else:
                still += 1
    lines = [
        "## A right citation in Arabic digits is scored wrong",
        "",
        f"{sum(rescued.values())} incorrect citations are the right verse once Arabic-Indic digits "
        f"are read as Western digits. {still} wrong citations stay wrong after that fold.",
        "",
    ]
    for model, n in sorted(rescued.items(), key=lambda item: -item[1]):
        lines.append(f"- {model}: {n}")
    if samples:
        lines += ["", "Examples:"]
        for model, gold, got in samples:
            lines.append(f"- {model}: expected `{gold}`, answered `{got}`")
    lines += [
        "",
        "The cite score asks for the same characters as the Latin citation in the question file. "
        "A model that answers in the digits of the Qur'an is counted as naming a different book. "
        "That is the benchmark under-crediting a correct location, which is the failure the scorer was built to avoid.",
        "",
    ]
    return lines


def _canon(run_dir: Path) -> list[str]:
    """Verify `yes` on a passage that belongs to another tradition."""
    answers = _answers(run_dir)
    lines = [
        "## Another canon, accepted as this one",
        "",
        "A verify `yes` on a `no` item means the model took a passage from somewhere else "
        "as the named edition. Across the finished files that happened twice.",
        "",
    ]
    found = 0
    for model, path in model_files(run_dir, "scores.jsonl"):
        for score in _rows(path):
            metrics = score.get("metrics") or {}
            if score.get("task") != "verify_source":
                continue
            if metrics.get("expected") != "no" or metrics.get("parsed") != "yes":
                continue
            answer = answers.get((model, score["question_id"]))
            if not answer:
                continue
            expected = (answer.get("question") or {}).get("expected") or {}
            prompt = (answer.get("question") or {}).get("prompt") or ""
            quote = ""
            if '"' in prompt:
                quote = prompt.split('"', 2)[1][:180]
            found += 1
            lines += [
                f"**{model}.** Asked whether this is the named edition, and said yes. "
                f"The passage is {expected.get('true_citation')} "
                f"({expected.get('true_tradition')}, {expected.get('true_version')}).",
                "",
                f"> {quote}",
                "",
                f"Answer: {(answer.get('answer') or '').strip().splitlines()[0][:240]}",
                "",
            ]
    if not found:
        lines.append("None in the finished files.")
        lines.append("")
    else:
        lines += [
            "qwen3-32b heard King James diction, `brethren` and `wroth`, and called a Book of Mormon verse the NRSV. "
            "Gemini Flash was asked if an NRSV sentence was the William Davidson Talmud. "
            "The sentence is Genesis 1:1. It said yes, and explained that this is the JPS Torah on Sefaria. "
            "That is three editions at once: the Talmud it was asked about, the Jewish translation it named, "
            "and the Christian translation it was actually shown. "
            "The creation verse is where the canons touch, and the model treated the touch as identity.",
            "",
        ]
    return lines


def _takeaway() -> list[str]:
    return [
        "## Takeaway",
        "",
        "One accuracy number ranks the wrong thing. It mixes three different facts: "
        "a habit of saying no, a prompt language that turns quoting and citing on and off, "
        "and a scorer that reads only Western digits. A model can reject every fake, "
        "quote a verse it cannot name, and write the right citation in Arabic digits, "
        "and the leaderboard will call the first knowledge and the third a miss.",
        "",
    ]


def _answered_rate(rows: list[dict], **match) -> tuple[int, int]:
    subset = [r for r in rows if all(r.get(key) == value for key, value in match.items())]
    correct, _incorrect, refused = _tally(subset)
    return correct, len(subset) - refused


def _pdf_text(x: float, y: float, size: int, text: str, font: str = "F1", gray: float = 0.15) -> str:
    safe = text.replace("\\", "").replace("(", "\\(").replace(")", "\\)")
    return f"BT /{font} {size} Tf {gray:.2f} g {x:.1f} {y:.1f} Td ({safe}) Tj ET"


def _bar(x: float, y: float, w: float, h: float, rgb: tuple[float, float, float]) -> str:
    red, green, blue = rgb
    return f"{x:.1f} {y:.1f} {w:.1f} {h:.1f} re {red:.2f} {green:.2f} {blue:.2f} rg f"


def _figure(rows: list[dict]) -> bytes:
    """Two panels: verify yes against no, and Gemini quote against cite."""
    page_w, page_h = 792, 560
    commands = [
        "0.98 0.98 0.97 rg",
        f"0 0 {page_w} {page_h} re f",
        _pdf_text(36, 524, 16, "One accuracy number ranks the wrong thing", "F2", 0.1),
        _pdf_text(36, 506, 9, "Finished files only. Percents exclude refusals.", "F1", 0.35),
    ]
    commands.append(_pdf_text(36, 476, 11, "Saying no is easier than recognizing the real text", "F2", 0.12))
    models = []
    for model in ("gemini-flash", "haiku", "qwen3-32b", "gpt-oss-20b"):
        yes_ok, yes_n = _answered_rate(rows, model=model, task="verify_source", expected_yn="yes")
        no_ok, no_n = _answered_rate(rows, model=model, task="verify_source", expected_yn="no")
        if yes_n or no_n:
            models.append((model, yes_ok, yes_n, no_ok, no_n))
    max_w = 150
    y = 448
    commands.append(_pdf_text(168, y + 16, 8, "real text", "F1", 0.25))
    commands.append(_pdf_text(330, y + 16, 8, "a fake", "F1", 0.25))
    for model, yes_ok, yes_n, no_ok, no_n in models:
        commands.append(_pdf_text(36, y, 9, model, "F1", 0.15))
        for origin, ok, n, color in (
            (160, yes_ok, yes_n, (0.25, 0.45, 0.72)),
            (322, no_ok, no_n, (0.75, 0.45, 0.28)),
        ):
            rate = 0 if not n else ok / n
            commands.append(_bar(origin, y - 2, max_w * rate, 12, color))
            commands.append(_pdf_text(origin + max_w * rate + 4, y, 8, _pct(ok, n), "F1", 0.2))
        y -= 28

    commands.append(_pdf_text(36, y - 8, 11, "Gemini Flash: quoting and citing switch with the prompt", "F2", 0.12))
    y -= 36
    wanted = [
        ("islam/native/population/prompt-native", "Qur'an, Arabic prompt"),
        ("islam/native/population/prompt-english", "Qur'an, English prompt"),
        ("christianity/native/masoretic/population/prompt-native", "Hebrew text, Hebrew prompt"),
        ("christianity/native/masoretic/population/prompt-english", "Hebrew text, English prompt"),
        ("christianity/native/greek/population/prompt-english", "Greek text, English prompt"),
        ("christianity/english/population", "NRSV, English prompt"),
    ]
    commands.append(_pdf_text(250, y + 14, 8, "quote", "F1", 0.25))
    commands.append(_pdf_text(400, y + 14, 8, "cite", "F1", 0.25))
    for folder, label in wanted:
        quote_ok, quote_n = _answered_rate(rows, model="gemini-flash", folder=folder, task="retrieve_quote")
        cite_ok, cite_n = _answered_rate(rows, model="gemini-flash", folder=folder, task="cite_passage")
        if not quote_n and not cite_n:
            continue
        commands.append(_pdf_text(36, y, 8, label, "F1", 0.15))
        for origin, ok, n, color in (
            (230, quote_ok, quote_n, (0.20, 0.50, 0.42)),
            (380, cite_ok, cite_n, (0.45, 0.32, 0.62)),
        ):
            rate = 0 if not n else ok / n
            commands.append(_bar(origin, y - 2, 120 * rate, 11, color))
            commands.append(_pdf_text(origin + 124, y, 8, _pct(ok, n), "F1", 0.2))
        y -= 24
    commands.append(_pdf_text(
        36, 28, 8,
        "Blue is recognizing the real verse. Orange is rejecting a fake. Green is quotation. Purple is citation.",
        "F1", 0.35,
    ))
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


def _story() -> list[str]:
    return [
        "## The story",
        "",
        "A leaderboard of theological accuracy will rank the wrong thing.",
        "",
        "The careful model refuses. Refusal is removed from accuracy, so the model that declines the hard verse "
        "outranks the model that answers it and is wrong. On verify, the easy point is saying no to a passage "
        "from somewhere else. The hard point is recognizing the real verse. gpt-oss-20b takes every easy point "
        "in the finished file and misses most of the real ones. Published as one accuracy, that is knowledge. "
        "It is a preference for no.",
        "",
        "The fluent model can quote a verse it cannot cite, or cite a verse it cannot quote. Gemini Flash, "
        "given the Qur'an in Arabic, does both. Given the same verses in English, it still quotes them and "
        "almost never names them. Given the Hebrew text in Hebrew, it names every verse and quotes none. "
        "The prompt language is choosing which skill is visible. A single Christianity number averages those "
        "into a tradition the model does not have.",
        "",
        "And the score itself has a script. A citation written with Arabic digits is the right verse and a wrong "
        "answer. The benchmark then reports that the model does not know where the verse is. The finding and "
        "the instrument have to be read together, or the paper ranks a refusal policy, a prompt language, "
        "and a Latin-digit rule.",
        "",
        "The negative item is not one test either. A Guru Granth Sahib question shown Arabic, or a "
        "Pali verse shown Gurmukhi, is an alphabet check. A Talmud question shown the Bible, and a "
        "Book of Mormon question shown a papal encyclical, are canon checks. One verify accuracy "
        "gives the alphabet check and the canon check the same weight.",
        "",
    ]


def main(
    run_dir: Annotated[str, typer.Option(help="run root holding <model>/base/**, such as runs/rerun-2026-11-03")],
    allow_partial: Annotated[
        bool, typer.Option(help="write the findings even when some answer rows have no question")
    ] = False,
) -> None:
    runs = resolve_run_dir(run_dir)
    questions = population_questions()
    matched, total = check_coverage(runs, questions, allow_partial)
    rows = _load(runs)
    if not rows:
        raise SystemExit(f"no scores.jsonl under {runs}/<model>/base/")
    shown = runs.relative_to(ROOT) if runs.is_relative_to(ROOT) else runs
    text = "\n".join(
        [
            "# Findings",
            "",
            f"From {len(rows)} scored answers in finished files in `{shown}`. "
            f"A file still being collected is not here.{partial_note(matched, total)}",
            "",
            *_takeaway(),
            *_story(),
            *_verify(rows),
            *_instrument(rows, questions),
            *_dissociation(rows),
            *_near(rows),
            *_digits(runs),
            *_canon(runs),
        ]
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    figure = OUT.parent / "takeaway.pdf"
    figure.write_bytes(_figure(rows))
    for path in (OUT, figure):
        print(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)


if __name__ == "__main__":
    typer.run(main)
