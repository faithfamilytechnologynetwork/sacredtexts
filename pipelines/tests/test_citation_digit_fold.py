"""Issue #111: a cite_passage answer written in native-script numerals is read as the number.

The native-text prompts end "Answer in the language of the Uthmani Qur'an / the Bhagavad Gita",
so a model rightly writes ``٣٤:٤٦`` for 34:46 or ``१०:३६`` for 10:36. A citation is a number:
every Unicode decimal digit (``Nd``) is read as its ASCII digit, in the citation path only.
Labels are not translated ("numerals only"), ``normalize()`` keeps the digits as they are, and
text retrieval / verify_source never see the fold.

The oracle at the bottom re-scores the committed 2026-11-02 cite_passage answers. The only cells
whose committed (pre-#111) scores differ from the #111 scorer are the ones registered by identity in
``testdata/citation_digit_fold_movers.tsv``, and none of them loses credit. Read-only; the committed
``scores.jsonl`` are not rewritten.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pytest

from sacredbench.score import _single_citation_correct, _with_outcome, fold_citation_digits, normalize, score_answer

RUNS = Path(__file__).resolve().parents[2] / "runs"
MOVERS = Path(__file__).parent / "testdata" / "citation_digit_fold_movers.tsv"


def _cite(answer: str, citation: str) -> dict:
    return score_answer("cite_passage", answer, {"citation": citation})


@pytest.mark.parametrize(
    "answer",
    [
        "٣٤:٤٦",  # Arabic-Indic — the reported cell (opus, question 22cc885a392180a2)
        "۳۴:۴۶",  # Extended Arabic-Indic (Persian/Urdu)
        "३४:४६",  # Devanagari
        "੩੪:੪੬",  # Gurmukhi
        "৩৪:৪৬",  # Bengali
        "3٤:4٦",  # mixed
        "**٣٤:٤٦**",
    ],
)
def test_native_numerals_are_the_same_citation(answer):
    scored = _cite(answer, "34:46")
    assert scored == {"correct": 1, "n_candidates": 1, "outcome": "correct"}


def test_devanagari_gita_citation():
    assert _cite("१०:३६", "10:36")["outcome"] == "correct"


def test_the_fold_is_symmetric():
    # Every committed expected citation is ASCII; a native-numeral ground truth must still match.
    assert _cite("34:46", "٣٤:٤٦")["outcome"] == "correct"
    assert _cite("٣٤:٤٦", "३४:४६")["outcome"] == "correct"
    assert _cite("34:47", "٣٤:٤٦")["outcome"] == "incorrect"


def test_one_citation_in_two_numeral_systems_is_not_a_hedge():
    # Pre-#111 these were two distinct candidates, so a hedge.
    assert _cite("१०:३ (or 10:3)", "10:3") == {"correct": 1, "n_candidates": 1, "outcome": "correct"}
    assert _cite("هذا في سورة التحريم، الآية الأولى: ٦٦:١\n\nفالجواب:\n\n66:1", "66:1")["outcome"] == "correct"


@pytest.mark.parametrize(
    ("answer", "citation"),
    [
        ("٣٤:٤٧", "34:46"),  # wrong verse
        ("٤٦:٣٤", "34:46"),  # reversed
        ("٣٤:٤٦٥", "34:46"),  # boundary: 34:465 is not 34:46
        ("١٣٤:٤٦", "34:46"),  # boundary on the left
        ("ਅੰਗ ੩੦੮:੧੩.", "Ang 306:13"),  # wrong ang (astra, committed)
    ],
)
def test_wrong_or_differently_labelled_citations_stay_incorrect(answer, citation):
    assert _cite(answer, citation)["outcome"] == "incorrect"


def test_two_different_native_citations_are_still_a_hedge():
    scored = _cite("٣٤:٤٦ or ٣٤:٤٧", "34:46")
    assert scored["n_candidates"] == 2 and scored["correct"] == 0


def test_fold_citation_digits():
    assert fold_citation_digits("٣٤:٤٦ ۳۴ ३४ ੩੪ ৩৪") == "34:46 34 34 34 34"
    for text in ("Jude 1:3", "Ang 734:8", "Sahih Muslim 2109a", "سورة سبأ", "भगवद्गीता"):
        assert fold_citation_digits(text) == text


def test_shared_normalize_and_other_tasks_do_not_fold():
    assert normalize("٣٤:٤٦") == "٣٤ ٤٦" != normalize("34:46")  # the shared normaliser keeps the digits
    assert score_answer("retrieve_quote", "٣٤", {"text": "34"})["correct"] == 0
    assert score_answer("complete_unit", "१०", {"text": "10"})["correct"] == 0


# --- oracle over the committed 2026-11-02 run ------------------------------------------------

# A surah-named citation (آل عمران: ١٤٠) and a Gurmukhi-labelled one (ਅੰਗ ੭੩੪:੮) stay incorrect under
# this layer; #112 credits them (test_citation_equivalence.py).


def _digit_fold_layer(answer: str, expected: dict) -> dict:
    """The #111 matcher alone. The #112 equivalence layer above it is pinned by its own oracle
    (test_citation_equivalence.py), so this one keeps pinning only the digit fold."""
    correct, n = _single_citation_correct(answer, expected["citation"])
    return _with_outcome({"correct": correct, "n_candidates": n}, "cite_passage", answer, expected)


# The registered moves: only these keys may change.
_MOVE_KEYS = {"correct", "outcome", "n_candidates"}


def _registered() -> dict[tuple[str, int, str], tuple[str, str, int, int]]:
    """(folder, row in answers.jsonl, question_id) -> (old outcome, new outcome, old n, new n). The row
    is part of the identity because a committed file can hold one question twice."""
    rows = [l.split("\t") for l in MOVERS.read_text(encoding="utf-8").splitlines() if l and not l.startswith("#")]
    registered = {
        (folder, int(row), qid): (old, new, int(old_n), int(new_n)) for folder, row, qid, old, new, old_n, new_n in rows
    }
    assert len(registered) == len(rows)
    return registered


def test_registered_mover_counts():
    by_kind = Counter(
        (folder.split("/", 2)[2], f"{old}->{new}") for (folder, _, _), (old, new, _, _) in _registered().items()
    )
    assert by_kind == {
        ("islam/native/population/prompt-english", "incorrect->correct"): 202,
        ("hinduism/native/population/prompt-english", "incorrect->correct"): 193,
        ("hinduism/native/population/prompt-native", "incorrect->correct"): 1,
        ("islam/native/population/prompt-english", "incorrect->incorrect"): 8,
        ("hinduism/native/population/prompt-english", "incorrect->incorrect"): 10,
    }
    for old, new, old_n, new_n in _registered().values():
        assert old != "correct"  # credit-only
        assert new == "correct" or new_n < old_n  # a stay-incorrect mover only merges candidates


def test_committed_cite_passage_cells_move_only_as_registered():
    registered = _registered()
    score_files = sorted(RUNS.glob("*/base/**/scores.jsonl"))
    if not score_files:
        pytest.skip("runs/ evidence not present")
    seen: set[tuple[str, int, str]] = set()
    for scores in score_files:
        folder = scores.parent.relative_to(RUNS).as_posix()
        answers = [json.loads(l) for l in scores.with_name("answers.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
        committed = [json.loads(l) for l in scores.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(answers) == len(committed), folder  # score_file keeps row order, so pair by position
        for i, (row, old) in enumerate(zip(answers, committed)):
            if row["task"] != "cite_passage":
                continue
            assert row["question_id"] == old["question_id"], folder
            new = _digit_fold_layer(row["answer"], row["question"]["expected"])
            key = (folder, i, row["question_id"])
            if key not in registered:
                assert new == old["metrics"], f"{key} moved but is not registered"
                continue
            seen.add(key)
            old_outcome, new_outcome, old_n, new_n = registered[key]
            assert (new["outcome"], new["n_candidates"]) == (new_outcome, new_n), key
            if new != old["metrics"]:  # not yet re-scored under #111
                changed = {k for k in new.keys() | old["metrics"].keys() if new.get(k) != old["metrics"].get(k)}
                assert changed <= _MOVE_KEYS, (key, changed)
                assert (old["metrics"]["outcome"], old["metrics"]["n_candidates"]) == (old_outcome, old_n), key
    assert seen == set(registered), f"registered cells missing from runs/: {sorted(set(registered) - seen)[:5]}"
