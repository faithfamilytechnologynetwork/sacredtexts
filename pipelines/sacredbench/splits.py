"""Splits the stored run asked for after the pooled tables.

Per-model accuracy inside each text, refusals by text rather than by language,
near copies by language, and a Fisher exact test of the Qur'an against Sahih
al-Bukhari on the two tasks that do not use a citation number. Nothing here
calls a model or changes a score.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from math import comb
from pathlib import Path

from sacredbench.failure_kind import (
    NEAR_COPY_F1,
    PARAPHRASE_F1,
    _expected_text,
    _tokens,
    classify_failure,
)
from sacredbench.probes import _load_rows

# Broader than the narrow hedge phrase in probes. Counts English uncertainty
# that the leading-cue refusal rule still scores incorrect.
_UNCERTAIN_RE = re.compile(
    r"not (?:entirely )?sure|not certain|don'?t want to|could you|i can only|"
    r"i can'?t tell|no further",
    re.IGNORECASE,
)
_CITE_RE = re.compile(
    r"(?P<book>(?:[1-3]\s+)?[A-Za-z][A-Za-z .]*?)?\s*(?P<c>\d+)\s*:\s*(?P<v>\d+)"
)

_QUOTE_TASKS = ("retrieve_quote", "complete_unit")


def fisher_exact(correct_a: int, incorrect_a: int, correct_b: int, incorrect_b: int) -> float:
    """Two-sided Fisher exact probability for a 2 by 2 table of graded answers."""

    def hyper(a: int, b: int, c: int, d: int) -> float:
        return comb(a + b, a) * comb(c + d, c) / comb(a + b + c + d, a + c)

    observed = hyper(correct_a, incorrect_a, correct_b, incorrect_b)
    row_a = correct_a + incorrect_a
    row_b = correct_b + incorrect_b
    col_correct = correct_a + correct_b
    total = 0.0
    for a in range(max(0, col_correct - row_b), min(row_a, col_correct) + 1):
        b = row_a - a
        c = col_correct - a
        d = row_b - c
        if min(b, c, d) < 0:
            continue
        probability = hyper(a, b, c, d)
        if probability <= observed + 1e-15:
            total += probability
    return total


def _model_name(model_id: str) -> str:
    return model_id.rsplit("/", 1)[-1]


def _is_bukhari(source: dict) -> bool:
    work = source.get("work") or ""
    version = source.get("version") or ""
    return "Bukhari" in work or "Bukhari" in version


def _pool(source: dict) -> str:
    """Text pool for refusal counts. Bukhari stays inside hadith."""
    work = source.get("work") or ""
    document_type = source.get("document_type") or ""
    if "Qur" in work:
        return "quran"
    if document_type == "hadith_collection":
        return "hadith"
    if work == "The Bible":
        return "bible"
    if document_type == "talmud":
        return "talmud"
    return work or "other"


def _gap_pool(source: dict) -> str | None:
    if "Qur" in (source.get("work") or ""):
        return "quran"
    if _is_bukhari(source):
        return "bukhari"
    return None


def _counts(rows: list[dict]) -> Counter:
    return Counter(row["outcome"] for row in rows)


def _accuracy(counts: Counter) -> float | None:
    graded = counts["correct"] + counts["incorrect"]
    if graded == 0:
        return None
    return counts["correct"] / graded


def per_model_by_text(rows: list[dict]) -> list[dict]:
    grouped: dict[tuple, list] = defaultdict(list)
    for row in rows:
        source = row["source"]
        key = (source.get("work") or "", source.get("version") or "", _model_name(row["model"]))
        grouped[key].append(row)
    report = []
    for (work, version, model), group in sorted(grouped.items()):
        counts = _counts(group)
        report.append({
            "work": work,
            "version": version,
            "model": model,
            "correct": counts["correct"],
            "incorrect": counts["incorrect"],
            "refused": counts["refused"],
            "accuracy": _accuracy(counts),
        })
    return report


def refusals_by_text(rows: list[dict]) -> dict:
    """Refusals by text pool and by model, so an Arabic total is not the unit."""
    by_pool: dict[str, Counter] = defaultdict(Counter)
    by_model: dict[tuple, Counter] = defaultdict(Counter)
    for row in rows:
        pool = _pool(row["source"])
        model = _model_name(row["model"])
        by_pool[pool][row["outcome"]] += 1
        by_model[(pool, model)][row["outcome"]] += 1
        if pool == "bible":
            version = row["source"].get("version") or ""
            by_model[(f"bible:{version}", model)][row["outcome"]] += 1
        if _is_bukhari(row["source"]):
            by_model[("bukhari", model)][row["outcome"]] += 1
    return {"by_pool": by_pool, "by_model": by_model}


def near_copy_by_language(rows: list[dict]) -> Counter:
    counts: Counter = Counter()
    for row in rows:
        if row["outcome"] != "incorrect" or row["task"] not in _QUOTE_TASKS:
            continue
        metrics = row["metrics"]
        kind = classify_failure(
            task=row["task"],
            correct=False,
            refused=False,
            answer=row["answer"],
            expected=_expected_text(row["expected"]),
            token_f1=metrics.get("token_f1"),
            normalized=metrics.get("normalized"),
            contains_reference=metrics.get("contains_reference"),
            n_candidates=metrics.get("n_candidates"),
        )
        if kind != "near_copy":
            continue
        language = row["source"].get("language") or "unknown"
        counts[language] += 1
    return counts


def quran_bukhari_gap(rows: list[dict]) -> dict:
    """Graded quotation and completion, the tasks with no citation number."""
    tables: dict[tuple, Counter] = defaultdict(Counter)
    for row in rows:
        pool = _gap_pool(row["source"])
        if pool is None or row["task"] not in _QUOTE_TASKS:
            continue
        if row["outcome"] == "refused":
            continue
        tables[(pool, "both")][row["outcome"]] += 1
        tables[(pool, row["task"])][row["outcome"]] += 1
        tables[(pool, _model_name(row["model"]))][row["outcome"]] += 1

    def pair(label: str) -> dict:
        quran = tables[("quran", label)]
        bukhari = tables[("bukhari", label)]
        return {
            "label": label,
            "quran_correct": quran["correct"],
            "quran_incorrect": quran["incorrect"],
            "bukhari_correct": bukhari["correct"],
            "bukhari_incorrect": bukhari["incorrect"],
            "fisher": fisher_exact(
                quran["correct"], quran["incorrect"], bukhari["correct"], bukhari["incorrect"]
            ),
        }

    labels = ["both", *_QUOTE_TASKS]
    labels += sorted({key[1] for key in tables if key[0] == "quran" and key[1] not in labels})
    return {"tests": [pair(label) for label in labels]}


def other_script_uncertainty(rows: list[dict]) -> dict:
    """English uncertainty inside other-script answers, which stay incorrect."""
    total = uncertain = 0
    for row in rows:
        if row["outcome"] != "incorrect" or row["task"] not in _QUOTE_TASKS:
            continue
        metrics = row["metrics"]
        kind = classify_failure(
            task=row["task"],
            correct=False,
            refused=False,
            answer=row["answer"],
            expected=_expected_text(row["expected"]),
            token_f1=metrics.get("token_f1"),
            normalized=metrics.get("normalized"),
            contains_reference=metrics.get("contains_reference"),
            n_candidates=metrics.get("n_candidates"),
        )
        if kind != "other_script":
            continue
        total += 1
        if _UNCERTAIN_RE.search(row["answer"] or ""):
            uncertain += 1
    return {"other_script": total, "uncertain": uncertain}


def _quote_kind(row: dict, floor: float) -> str | None:
    if row["outcome"] != "incorrect" or row["task"] not in _QUOTE_TASKS:
        return None
    metrics = row["metrics"]
    kind = classify_failure(
        task=row["task"],
        correct=False,
        refused=False,
        answer=row["answer"],
        expected=_expected_text(row["expected"]),
        token_f1=metrics.get("token_f1"),
        normalized=metrics.get("normalized"),
        contains_reference=metrics.get("contains_reference"),
        n_candidates=metrics.get("n_candidates"),
    )
    if kind in ("other_script", "omission"):
        return kind
    f1 = metrics.get("token_f1") or 0
    if f1 >= NEAR_COPY_F1:
        return "near_copy"
    if f1 >= floor:
        return "paraphrase"
    return "wrong_passage"


def sensitivity(rows: list[dict]) -> dict:
    """Cutoff moves and the accuracy change if refusals count as incorrect."""
    floors = {}
    for floor in (0.3, PARAPHRASE_F1, 0.6):
        counts: Counter = Counter()
        for row in rows:
            kind = _quote_kind(row, floor)
            if kind:
                counts[kind] += 1
        floors[f"{floor:.1f}"] = dict(counts)
    addition = {4: 0, 8: 0, 12: 0}
    for row in rows:
        if row["outcome"] != "correct" or row["task"] not in _QUOTE_TASKS:
            continue
        metrics = row["metrics"]
        if metrics.get("contains_reference") != 1 or metrics.get("normalized") == 1:
            continue
        extra = len(_tokens(row["answer"])) - len(_tokens(_expected_text(row["expected"])))
        for bar in addition:
            if extra >= bar:
                addition[bar] += 1
    by_model: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        by_model[_model_name(row["model"])][row["outcome"]] += 1
    models = []
    for model, counts in sorted(by_model.items()):
        graded = counts["correct"] + counts["incorrect"]
        with_refusals = graded + counts["refused"]
        models.append({
            "model": model,
            "accuracy": counts["correct"] / graded if graded else None,
            "refusals_as_incorrect": counts["correct"] / with_refusals if with_refusals else None,
        })
    return {"floors": floors, "addition": addition, "models": models}


def _canon_book(name: str, books: list[str]) -> str:
    name = name.replace("psalm", "psalms")
    for book in books:
        if name == book or name.startswith(book) or (book.startswith(name) and len(name) > 3):
            return book
    return name


def citation_distance(rows: list[dict], quran: set[str], bible: set[tuple[str, int, int]]) -> Counter:
    """How far a one-candidate Bible or Qur'an citation sits from the gold verse."""
    books = sorted({book for book, _, _ in bible}, key=len, reverse=True)
    counts: Counter = Counter()
    for row in rows:
        if row["task"] != "cite_passage" or row["outcome"] != "incorrect":
            continue
        if row["metrics"].get("n_candidates") != 1:
            continue
        work = row["source"].get("work")
        if work not in ("The Qur'an", "The Bible"):
            continue
        gold = _CITE_RE.search(row["source"].get("citation") or "")
        answer = (row["answer"] or "").replace("\u202f", " ").replace("\xa0", " ")
        pred = _CITE_RE.search(answer)
        if not gold or not pred:
            counts[(work, "unparsed")] += 1
            continue
        gc, gv = int(gold.group("c")), int(gold.group("v"))
        ac, av = int(pred.group("c")), int(pred.group("v"))
        if work == "The Qur'an":
            exists = f"{ac}:{av}" in quran
            same_book = True
        else:
            gb = _canon_book((gold.group("book") or "").strip().lower().rstrip("."), books)
            ab = _canon_book((pred.group("book") or "").strip().lower().rstrip("."), books)
            exists = (ab, ac, av) in bible
            same_book = gb == ab
        same_chapter = same_book and ac == gc
        if not exists:
            label = "not in this text"
        elif same_chapter and abs(av - gv) == 1:
            label = "adjacent verse"
        elif same_chapter:
            label = "same chapter"
        elif same_book:
            label = "same book, other chapter"
        else:
            label = "other book"
        counts[(work, label)] += 1
    return counts


def _load_quran(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    data = json.loads(path.read_text())
    return set(data) if isinstance(data, dict) else set()


def _load_bible(path: Path) -> set[tuple[str, int, int]]:
    if not path.is_file():
        return set()
    rows = json.loads(path.read_text())
    return {(row["book"].lower(), int(row["chapter"]), int(row["verse"])) for row in rows}


def split_run(
    run_dir: Path,
    quran_path: Path | None = None,
    bible_path: Path | None = None,
) -> dict:
    rows = _load_rows(run_dir)
    return {
        "per_model": per_model_by_text(rows),
        "refusals": refusals_by_text(rows),
        "near_copy": near_copy_by_language(rows),
        "gap": quran_bukhari_gap(rows),
        "other_script": other_script_uncertainty(rows),
        "sensitivity": sensitivity(rows),
        "citation_distance": citation_distance(
            rows,
            _load_quran(quran_path) if quran_path else set(),
            _load_bible(bible_path) if bible_path else set(),
        ),
    }


def _fmt_rate(counts: Counter) -> str:
    graded = counts["correct"] + counts["incorrect"]
    accuracy = _accuracy(counts)
    accuracy_s = "n/a" if accuracy is None else f"{accuracy:.3f}"
    n = sum(counts.values())
    refused = counts["refused"]
    refusal = "n/a" if n == 0 else f"{refused / n:.3f}"
    return (
        f"C{counts['correct']} I{counts['incorrect']} R{refused} "
        f"acc={accuracy_s} refusal={refusal} graded={graded}"
    )


def format_splits(report: dict) -> str:
    lines = ["per model inside each text"]
    for row in report["per_model"]:
        accuracy = "n/a" if row["accuracy"] is None else f"{row['accuracy']:.3f}"
        lines.append(
            f"  {row['work']} [{row['version']}] {row['model']}: "
            f"C{row['correct']} I{row['incorrect']} R{row['refused']} acc={accuracy}"
        )
    lines.append("refusals by text, not by language")
    refusals = report["refusals"]
    for pool, counts in sorted(refusals["by_pool"].items()):
        lines.append(f"  {pool}: {_fmt_rate(counts)}")
    lines.append("refusals by text and model")
    for (pool, model), counts in sorted(refusals["by_model"].items()):
        lines.append(f"  {pool} {model}: {_fmt_rate(counts)}")
    lines.append("near copies by language")
    near = report["near_copy"]
    if not near:
        lines.append("  none")
    for language, count in sorted(near.items()):
        lines.append(f"  {language}: {count}")
    lines.append("Qur'an vs Bukhari on tasks with no citation number (Fisher exact)")
    for test in report["gap"]["tests"]:
        lines.append(
            f"  {test['label']}: "
            f"Qur'an {test['quran_correct']}/{test['quran_correct'] + test['quran_incorrect']} "
            f"Bukhari {test['bukhari_correct']}/{test['bukhari_correct'] + test['bukhari_incorrect']} "
            f"p={test['fisher']:.4f}"
        )
    other = report["other_script"]
    lines.append(
        "other script that says it is unsure or asks for a number: "
        f"{other['uncertain']} of {other['other_script']}"
    )
    sens = report["sensitivity"]
    lines.append("paraphrase floor on incorrect quotations and completions")
    for floor, counts in sens["floors"].items():
        lines.append(
            f"  floor {floor}: near_copy={counts.get('near_copy', 0)} "
            f"paraphrase={counts.get('paraphrase', 0)} "
            f"wrong_passage={counts.get('wrong_passage', 0)} "
            f"omission={counts.get('omission', 0)} "
            f"other_script={counts.get('other_script', 0)}"
        )
    add = sens["addition"]
    lines.append(
        "correct quotes with extra tokens: "
        + " ".join(f">={bar}:{add[bar]}" for bar in sorted(add))
    )
    lines.append("accuracy if refusals count as incorrect")
    for row in sens["models"]:
        lines.append(
            f"  {row['model']}: {row['accuracy']:.3f} -> {row['refusals_as_incorrect']:.3f}"
        )
    lines.append("wrong citation distance, one candidate, Bible and Qur'an")
    distance = report["citation_distance"]
    if not distance:
        lines.append("  no verse index, or no such citations")
    for (work, label), count in sorted(distance.items()):
        lines.append(f"  {work} / {label}: {count}")
    return "\n".join(lines)
