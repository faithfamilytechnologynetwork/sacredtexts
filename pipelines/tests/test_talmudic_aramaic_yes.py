"""Issue #128: in Talmudic Aramaic a stand-alone ``אִין`` is "yes" (the Gemara's ``אִין`` / ``לָא`` pair). It
was listed as Hebrew "no" ("there is not"), and ``_strip_marks`` removes the hiriq that separates ``אִין``
from ``אֵין``, so every Aramaic "yes" was read as "no". It is now a yes-word.

Premise correction: the issue keyed the fix on ``arc`` cells, but the Talmud (William Davidson Aramaic)
cells are tagged ``source.language: "he"``, Sefaria's Hebrew-script tag. ``arc`` is only the Masoretic
Aramaic portions. Since every non-Latin native word is read on every cell (#95), ``אין`` is "yes" on
every cell, as Syriac ``ܐܝܢ`` already is. It must still stand alone: ``אין לי גישה`` ("I have no access")
is no verdict.

The registered set was derived by running the pre-#128 and #128 parsers over every verify_source answer
under ``runs/`` and is pinned here by identity. Every mover is a stand-alone leading ``אין`` on a Talmud
Aramaic English-prompt cell ("Answer in the language of the William Davidson Aramaic edition"):

- 74 cells in committed ``scores.jsonl``: 73 expected-yes ``incorrect`` → ``correct``, and beam's ``אִין``
  to a Jeremiah verse (expected no) ``correct`` → ``incorrect``.
- 67 cells in the untracked ``runs/rerun-2026-11-03``: 66 → ``correct``, 1 (the same beam answer) →
  ``incorrect``. The rerun is a witness, not a gate: each folder skips when absent.
- ``runs/archive``, every Masoretic cell, every other corpus: none.

No committed ``scores.jsonl`` is rewritten. The scan over committed scores is in
``test_cross_language_verdict_rebaseline.py``, which accepts these cells. Read-only.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pytest

from sacredbench.score import parse_yes_no, score_answer

RUNS = Path(__file__).resolve().parents[2] / "runs"
RERUN = "rerun-2026-11-03"


@pytest.mark.parametrize(
    "answer, language",
    [
        ("אין", "arc"),
        ("אין", "he"),                     # the Talmud cells are tagged "he"
        ("אִין", "he"),
        ("אין.", "he"),
        ("**אין**", "he"),
        ("**אִין**. מַסֶּכֶת רֹאשׁ הַשָּׁנָה כ״א ע״א.", "he"),
        ("אין", "en"),                     # a non-Latin word is read on every cell (#95)
    ],
)
def test_aramaic_in_is_yes(answer, language):
    assert parse_yes_no(answer, language) == "yes"


@pytest.mark.parametrize("answer, language", [("לא", "arc"), ("לָא.", "arc"), ("לאו", "he"), ("לא", "he")])
def test_aramaic_and_hebrew_no_words_stay_no(answer, language):
    assert parse_yes_no(answer, language) == "no"


@pytest.mark.parametrize(
    "answer, language",
    [
        ("אין לי גישה", "arc"),           # "I have no access": a following word, not a verdict
        ("אין לי גישה לנוסח המדויק", "he"),
        ("אין בידי לאמת", "he"),
    ],
)
def test_in_followed_by_a_word_is_not_a_verdict(answer, language):
    assert parse_yes_no(answer, language) is None


# answers folder (relative to runs/) -> {question_id: outcome under #128}. A registered cell moves between
# correct and incorrect; nothing moves into or out of refused.
FLIPS: dict[str, dict[str, str]] = {
    "argon/base/judaism/native/population/prompt-english": {
        "045f53ff31bbc451": "correct", "0d9a38c5c17e376a": "correct", "109c9dba2300dda6": "correct",
        "16483a19c77ad1df": "correct", "194b9ceddcd819f7": "correct", "253a91c24af287ee": "correct",
        "322a7708ee6499ab": "correct", "35b058fb8cf731a2": "correct", "3c94f2e8a8150c23": "correct",
        "42db23be5ed58b5a": "correct", "6840ae7b70f63f33": "correct", "7bf03aa4140a7936": "correct",
        "97111049a35a5ee6": "correct", "ce7d2c8f95c2b5b4": "correct",
    },
    "astra/base/judaism/native/population/prompt-english": {
        "045f53ff31bbc451": "correct", "0d9a38c5c17e376a": "correct", "194b9ceddcd819f7": "correct",
        "322a7708ee6499ab": "correct", "35b058fb8cf731a2": "correct", "42db23be5ed58b5a": "correct",
    },
    "beam/base/judaism/native/population/prompt-english": {
        "104f6f2dcc356ab7": "correct", "122e8950a7783ac3": "incorrect", "16483a19c77ad1df": "correct",
        "194b9ceddcd819f7": "correct", "6840ae7b70f63f33": "correct", "97111049a35a5ee6": "correct",
        "ce7d2c8f95c2b5b4": "correct",
    },
    "fable/base/judaism/native/population/prompt-english": {
        "045f53ff31bbc451": "correct", "104f6f2dcc356ab7": "correct", "109c9dba2300dda6": "correct",
        "16483a19c77ad1df": "correct", "194b9ceddcd819f7": "correct", "322a7708ee6499ab": "correct",
        "3c94f2e8a8150c23": "correct", "42db23be5ed58b5a": "correct", "6840ae7b70f63f33": "correct",
        "97111049a35a5ee6": "correct",
    },
    "gemini-flash/base/judaism/native/population/prompt-english": {
        "045f53ff31bbc451": "correct", "0d9a38c5c17e376a": "correct", "104f6f2dcc356ab7": "correct",
        "109c9dba2300dda6": "correct", "16483a19c77ad1df": "correct", "194b9ceddcd819f7": "correct",
        "253a91c24af287ee": "correct", "322a7708ee6499ab": "correct", "35b058fb8cf731a2": "correct",
        "3c94f2e8a8150c23": "correct", "42db23be5ed58b5a": "correct", "7bf03aa4140a7936": "correct",
        "97111049a35a5ee6": "correct", "ce7d2c8f95c2b5b4": "correct",
    },
    "opus/base/judaism/native/population/prompt-english": {
        "045f53ff31bbc451": "correct", "0d9a38c5c17e376a": "correct", "104f6f2dcc356ab7": "correct",
        "109c9dba2300dda6": "correct", "16483a19c77ad1df": "correct", "194b9ceddcd819f7": "correct",
        "253a91c24af287ee": "correct", "322a7708ee6499ab": "correct", "35b058fb8cf731a2": "correct",
        "3c94f2e8a8150c23": "correct", "42db23be5ed58b5a": "correct", "6840ae7b70f63f33": "correct",
        "7bf03aa4140a7936": "correct", "97111049a35a5ee6": "correct", "ce7d2c8f95c2b5b4": "correct",
    },
    "rerun-2026-11-03/argon/base/judaism/native/population/prompt-english": {
        "1ad8e0e1134339f5": "correct", "39ddd585d08cd19b": "correct", "5d6047f35a5f3b58": "correct",
        "6a6131a6b4ff3b96": "correct", "983e06f8585f7b81": "correct", "99bc3590cea6d244": "correct",
        "a1fd261266f105a1": "correct", "a2f15831fd97d359": "correct", "bedcb00dd5028f6d": "correct",
        "c5c18bc46f5a304f": "correct", "cd45bd9156cb42c2": "correct", "ce050718836c09fb": "correct",
        "d64e1773d5e5a8e3": "correct", "ee604069a4331f8c": "correct", "fdbadb53c23362a8": "correct",
    },
    "rerun-2026-11-03/astra/base/judaism/native/population/prompt-english": {
        "99bc3590cea6d244": "correct", "bedcb00dd5028f6d": "correct", "ce050718836c09fb": "correct",
    },
    "rerun-2026-11-03/beam/base/judaism/native/population/prompt-english": {
        "5d6047f35a5f3b58": "correct", "99bc3590cea6d244": "correct", "a1fd261266f105a1": "correct",
        "a2f15831fd97d359": "correct", "c5c18bc46f5a304f": "correct", "ce050718836c09fb": "correct",
        "e884c1bbd9dd5e5e": "incorrect", "ee604069a4331f8c": "correct",
    },
    "rerun-2026-11-03/fable/base/judaism/native/population/prompt-english": {
        "1ad8e0e1134339f5": "correct", "39ddd585d08cd19b": "correct", "5d6047f35a5f3b58": "correct",
        "6a6131a6b4ff3b96": "correct", "983e06f8585f7b81": "correct", "99bc3590cea6d244": "correct",
        "c5c18bc46f5a304f": "correct", "ce050718836c09fb": "correct", "fdbadb53c23362a8": "correct",
    },
    "rerun-2026-11-03/gemini-flash/base/judaism/native/population/prompt-english": {
        "39ddd585d08cd19b": "correct", "983e06f8585f7b81": "correct", "99bc3590cea6d244": "correct",
        "a2f15831fd97d359": "correct", "bedcb00dd5028f6d": "correct", "c5c18bc46f5a304f": "correct",
        "cd45bd9156cb42c2": "correct", "ee604069a4331f8c": "correct", "fdbadb53c23362a8": "correct",
    },
    "rerun-2026-11-03/opus/base/judaism/native/population/prompt-english": {
        "1ad8e0e1134339f5": "correct", "39ddd585d08cd19b": "correct", "6a6131a6b4ff3b96": "correct",
        "983e06f8585f7b81": "correct", "99bc3590cea6d244": "correct", "a1fd261266f105a1": "correct",
        "a2f15831fd97d359": "correct", "bedcb00dd5028f6d": "correct", "c5c18bc46f5a304f": "correct",
        "cd45bd9156cb42c2": "correct", "ce050718836c09fb": "correct", "d64e1773d5e5a8e3": "correct",
        "ee604069a4331f8c": "correct", "fdbadb53c23362a8": "correct",
    },
    "rerun-2026-11-03/sol/base/judaism/native/population/prompt-english": {
        "39ddd585d08cd19b": "correct", "6a6131a6b4ff3b96": "correct", "a1fd261266f105a1": "correct",
        "a2f15831fd97d359": "correct", "ce050718836c09fb": "correct", "fdbadb53c23362a8": "correct",
    },
    "rerun-2026-11-03/terra/base/judaism/native/population/prompt-english": {
        "1ad8e0e1134339f5": "correct", "5d6047f35a5f3b58": "correct", "6a6131a6b4ff3b96": "correct",
    },
    "sol/base/judaism/native/population/prompt-english": {
        "045f53ff31bbc451": "correct", "109c9dba2300dda6": "correct", "253a91c24af287ee": "correct",
        "322a7708ee6499ab": "correct", "35b058fb8cf731a2": "correct", "97111049a35a5ee6": "correct",
        "ce7d2c8f95c2b5b4": "correct",
    },
    "terra/base/judaism/native/population/prompt-english": {
        "ce7d2c8f95c2b5b4": "correct",
    },
}


def _verify_answers(folder: str) -> dict[str, dict] | None:
    path = RUNS / folder / "answers.jsonl"
    if not path.exists():
        return None
    rows = (json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    return {d["question_id"]: d for d in rows if d["task"] == "verify_source"}


def _score(d: dict) -> dict:
    q = d["question"]
    return score_answer("verify_source", d["answer"] or "", q["expected"], language=q["source"]["language"])


def test_registered_set_size():
    def outcomes(rerun: bool) -> Counter:
        return Counter(o for f, cells in FLIPS.items() if f.startswith(RERUN) == rerun for o in cells.values())

    assert outcomes(rerun=False) == {"correct": 73, "incorrect": 1}
    assert outcomes(rerun=True) == {"correct": 66, "incorrect": 1}


@pytest.mark.parametrize("folder", sorted(FLIPS))
def test_registered_cells_are_graded_as_registered(folder):
    answers = _verify_answers(folder)
    if answers is None:
        pytest.skip(f"{folder} evidence not present")
    for qid, outcome in FLIPS[folder].items():
        assert qid in answers, f"{folder}: registered cell {qid} has no verify_source answer"
        metrics = _score(answers[qid])
        assert metrics["parsed"] == "yes", (folder, qid, metrics)
        assert metrics["outcome"] == outcome, (folder, qid, metrics)


def test_rerun_moves_exactly_the_registered_cells():
    # The rerun was scored before #115, so its stored outcomes differ from a rescore for #115's cells
    # (refused -> graded). #128 is the only change that turns a stored "no" verdict into "yes": the
    # cells where that happens must be exactly the registered rerun set.
    root = RUNS / RERUN
    if not root.exists():
        pytest.skip(f"{RERUN} evidence not present")
    moved: set[tuple[str, str]] = set()
    for scores in sorted(root.rglob("scores.jsonl")):
        folder = str(scores.parent.relative_to(RUNS))
        answers = _verify_answers(folder)
        if answers is None:
            continue
        for line in scores.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if row["task"] == "verify_source" and row["metrics"]["parsed"] == "no":
                if _score(answers[row["question_id"]])["parsed"] != "no":
                    moved.add((folder, row["question_id"]))
    registered = {(f, q) for f, cells in FLIPS.items() if f.startswith(RERUN) for q in cells}
    assert moved == registered
