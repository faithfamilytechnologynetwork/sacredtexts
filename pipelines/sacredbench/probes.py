"""Checks on a stored run that do not call a model.

Each check answers one open question from the manuscript, or says the stored
files cannot answer it. Nothing here changes a score.
"""

from __future__ import annotations

import json
import random
import re
from collections import defaultdict
from pathlib import Path

from sacredbench.failure_kind import classify_failure, expected_text
from sacredbench.score import bounded_contains, normalize

# Letter forms normalize() does not decompose. Applied after normalize().
_LETTER_FOLD = str.maketrans({
    "أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا",
    "ى": "ي", "ئ": "ي", "ؤ": "و", "ة": "ه",
})

# English hedges the refusal cue list does not treat as a decline.
_HEDGE_RE = re.compile(
    r"\b(i can only|i'm not sure|i am not sure|not sure which|i cannot be sure|"
    r"i can't be sure|only reliably)\b"
)

# Words a hadith refusal might use if it is declining on attribution.
_AUTH_RE = re.compile(
    r"\b(isnad|isnād|chain of narration|authentic|authenticity|fabricat\w*|"
    r"attribution|cannot verify|can't verify|not a (?:sahih|sound) )\b",
    re.IGNORECASE,
)


def fold_arabic_letters(text: str) -> str:
    """normalize(), then map leftover alef, ya, and ta marbuta forms together."""
    return normalize(text).translate(_LETTER_FOLD)


def load_rows(run_dir: Path) -> list[dict]:
    answers = {}
    for line in (run_dir / "answers.jsonl").read_text().splitlines():
        if line.strip():
            row = json.loads(line)
            answers[(row["question_id"], row["model_id"])] = row
    rows = []
    for line in (run_dir / "scores.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        score = json.loads(line)
        answer_row = answers.get((score["question_id"], score["model_id"]))
        if answer_row is None:
            continue
        question = answer_row.get("question") or {}
        source = question.get("source") or {}
        metrics = score.get("metrics") or {}
        outcome = metrics.get("outcome")
        if outcome not in ("correct", "incorrect", "refused"):
            outcome = "correct" if metrics.get("correct") == 1 else "incorrect"
        rows.append({
            "task": score["task"],
            "model": score["model_id"],
            "qid": score["question_id"],
            "outcome": outcome,
            "answer": answer_row.get("answer") or "",
            "expected": question.get("expected") or {},
            "source": source,
            "metrics": metrics,
        })
    return rows


def _verse_index(path: Path) -> dict[str, str]:
    """Map ``Book chapter:verse`` to text for a raw Bible JSON list.

    Fail loud: a path that was passed (or defaulted) but does not exist is a usage error — the
    wrong working directory, a renamed payload — not a reason to silently report "0 of 0"."""
    if not path.is_file():
        raise FileNotFoundError(f"edition payload not found: {path}")
    rows = json.loads(path.read_text())
    out = {}
    for row in rows:
        key = f"{row['book']} {row['chapter']}:{row['verse']}"
        out[key] = row["text"]
    return out


def arabic_letter_fold(rows: list[dict]) -> dict:
    """How many incorrect Arabic quotations the extra letter fold would contain."""
    checked = flipped = 0
    for row in rows:
        if row["source"].get("language") != "ar":
            continue
        if row["task"] not in ("retrieve_quote", "complete_unit"):
            continue
        if row["outcome"] != "incorrect":
            continue
        expected = expected_text(row["expected"])
        checked += 1
        a = fold_arabic_letters(row["answer"])
        e = fold_arabic_letters(expected)
        if e and re.search(r"(?<!\w)" + re.escape(e) + r"(?!\w)", a):
            flipped += 1
    return {"incorrect_arabic_quotes": checked, "contained_after_letter_fold": flipped}


def clustered_accuracy(rows: list[dict], *, draws: int = 1000, seed: int = 0) -> dict:
    """Per text, accuracy with an interval from resampling questions, not answers.

    Each question keeps its model answers together, so three models on one item
    count as one draw.
    """
    by_text: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        source = row["source"]
        key = f"{source.get('work')} · {source.get('version')}"
        by_text[key][row["qid"]].append(row["outcome"])
    rng = random.Random(seed)
    out = {}
    for key, items in sorted(by_text.items()):
        qids = list(items)
        def acc(sample: list[str]) -> float | None:
            outcomes = [o for q in sample for o in items[q]]
            graded = [o for o in outcomes if o != "refused"]
            if not graded:
                return None
            return graded.count("correct") / len(graded)
        point = acc(qids)
        boots = []
        for _ in range(draws):
            sample = [rng.choice(qids) for _ in qids]
            value = acc(sample)
            if value is not None:
                boots.append(value)
        boots.sort()
        if boots:
            lo = boots[int(0.025 * (len(boots) - 1))]
            hi = boots[int(0.975 * (len(boots) - 1))]
        else:
            lo = hi = None
        out[key] = {"n_questions": len(qids), "accuracy": point, "low": lo, "high": hi}
    return out


def refusal_notes(rows: list[dict]) -> dict:
    """Count hadith refusals whose text names authenticity or attribution."""
    hadith = hedges = auth = 0
    for row in rows:
        if row["outcome"] != "refused":
            continue
        if row["source"].get("document_type") != "hadith_collection":
            continue
        hadith += 1
        if _AUTH_RE.search(row["answer"] or ""):
            auth += 1
    other = 0
    other_hedge = 0
    for row in rows:
        if row["outcome"] != "incorrect":
            continue
        if row["task"] not in ("retrieve_quote", "complete_unit"):
            continue
        expected = expected_text(row["expected"])
        kind = classify_failure(
            task=row["task"], correct=False, refused=False,
            answer=row["answer"], expected=expected,
            token_f1=row["metrics"].get("token_f1"),
            normalized=row["metrics"].get("normalized"),
            contains_reference=row["metrics"].get("contains_reference"),
            n_candidates=row["metrics"].get("n_candidates"),
        )
        if kind != "other_script":
            continue
        other += 1
        if _HEDGE_RE.search(normalize(row["answer"])):
            other_hedge += 1
            hedges += 1
    return {
        "hadith_refusals": hadith,
        "hadith_refusals_naming_authenticity": auth,
        "other_script": other,
        "other_script_with_english_hedge": other_hedge,
    }


def kjv_substitution(rows: list[dict], kjv: dict[str, str]) -> dict:
    """Incorrect ASV or WEB quotations that contain the KJV wording of that verse."""
    checked = hit = 0
    for row in rows:
        version = row["source"].get("version") or ""
        if "ASV" not in version and "WEB" not in version:
            continue
        if row["task"] not in ("retrieve_quote", "complete_unit") or row["outcome"] != "incorrect":
            continue
        citation = row["source"].get("citation") or ""
        gold = kjv.get(citation)
        if not gold:
            continue
        checked += 1
        if bounded_contains(row["answer"], gold):
            hit += 1
    return {"asv_web_incorrect_with_kjv_verse": checked, "answer_contains_kjv": hit}


def answer_length(rows: list[dict]) -> dict:
    """Extra tokens on correct quotations. The addition label starts at 8."""
    extras = []
    for row in rows:
        if row["outcome"] != "correct" or row["task"] not in ("retrieve_quote", "complete_unit"):
            continue
        expected = expected_text(row["expected"])
        extra = len(normalize(row["answer"]).split()) - len(normalize(expected).split())
        extras.append(extra)
    extras.sort()
    def at(p: float) -> int | None:
        if not extras:
            return None
        return extras[int(p * (len(extras) - 1))]
    return {
        "correct_quotes": len(extras),
        "extra_tokens_p50": at(0.5),
        "extra_tokens_p90": at(0.9),
        "at_least_8_extra": sum(1 for n in extras if n >= 8),
    }


def panel_note(run_dir: Path) -> dict:
    summary = run_dir / "summary.json"
    if not summary.is_file():
        return {}
    panel = json.loads(summary.read_text()).get("panel") or {}
    return {
        mid: {"model": info.get("model"), "endpoint": info.get("endpoint"), "tools": info.get("tools")}
        for mid, info in panel.items()
    }


def probe_run(run_dir: Path, kjv_path: Path | None = None) -> dict:
    rows = load_rows(run_dir)
    kjv = _verse_index(kjv_path) if kjv_path is not None else {}
    return {
        "panel": panel_note(run_dir),
        "arabic_letter_fold": arabic_letter_fold(rows),
        "intervals": clustered_accuracy(rows),
        "refusals": refusal_notes(rows),
        "kjv_substitution": kjv_substitution(rows, kjv),
        "answer_length": answer_length(rows),
        "hadith_numbering": (
            "Gold hadith citations are one stored number per item. "
            "This run has no second numbering scheme, so a wrong place cannot be "
            "reclassified as the same hadith under another edition's number."
        ),
    }


def format_probe(report: dict) -> str:
    lines = ["panel"]
    for mid, info in sorted(report["panel"].items()):
        lines.append(f"  {mid}: {info.get('model')} via {info.get('endpoint')} tools={info.get('tools')}")
    fold = report["arabic_letter_fold"]
    lines.append(
        "arabic letter fold: "
        f"{fold['contained_after_letter_fold']} of {fold['incorrect_arabic_quotes']} "
        "incorrect Arabic quotations become contained"
    )
    ref = report["refusals"]
    lines.append(
        "hadith refusals naming authenticity: "
        f"{ref['hadith_refusals_naming_authenticity']} of {ref['hadith_refusals']}"
    )
    lines.append(
        "other script with an English hedge the cue list missed: "
        f"{ref['other_script_with_english_hedge']} of {ref['other_script']}"
    )
    kjv = report["kjv_substitution"]
    lines.append(
        "ASV/WEB incorrect quotations that contain the KJV verse: "
        f"{kjv['answer_contains_kjv']} of {kjv['asv_web_incorrect_with_kjv_verse']}"
    )
    length = report["answer_length"]
    lines.append(
        "correct quotations extra tokens: "
        f"n={length['correct_quotes']} p50={length['extra_tokens_p50']} "
        f"p90={length['extra_tokens_p90']} at_least_8={length['at_least_8_extra']}"
    )
    lines.append(report["hadith_numbering"])
    lines.append("per text, questions clustered (accuracy, 95% resample interval)")
    for key, row in report["intervals"].items():
        acc = row["accuracy"]
        lo, hi = row["low"], row["high"]
        acc_s = "—" if acc is None else f"{acc:.3f}"
        span = "—" if lo is None else f"[{lo:.3f}, {hi:.3f}]"
        lines.append(f"  {key}: {acc_s} {span} ({row['n_questions']} questions)")
    return "\n".join(lines)
