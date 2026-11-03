"""A Devanagari avagraha (ऽ) is a spelling convention, not part of the words.

Gita Press prints ``चाऽऽचारो`` for च + आचारो; most printings, and every model in the committed
runs, write ``चाचारो``. A single ``ऽ`` (``तेऽपि``) is also often dropped. ``normalize()`` keeps the
sign, so a verse with the right words but the other spelling failed containment and scored
incorrect.

``fold_aware_contains`` now also compares the two with the avagraha removed, for a Devanagari
reference only. It is one more OR, so it only adds credit; ``normalize()`` and the equality
submetrics are unchanged.

The oracle at the bottom re-derives containment for every committed retrieve_quote / complete_unit
cell, fold off and fold on. The cells that move are exactly those registered by identity in
``testdata/devanagari_avagraha_movers.tsv``, and each goes from not contained to contained.
Read-only; the committed ``scores.jsonl`` are not rewritten.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import sacredbench.score as score_mod
from sacredbench.score import bounded_contains, fold_aware_contains, normalize, score_answer

RUNS = Path(__file__).resolve().parents[2] / "runs"
MOVERS = Path(__file__).parent / "testdata" / "devanagari_avagraha_movers.tsv"

GITA_16_7 = "न शौचं नापि चाऽऽचारो न सत्यं तेषु विद्यते"  # Gita Press, as the corpus holds it


def test_the_reported_cell_is_credited():
    # 42cea940d27328f3, complete_unit, Bhagavad Gita 16:7: every FAccT model wrote चाचारो.
    answer = "न शौचं नापि चाचारो न सत्यं तेषु विद्यते॥"
    assert not bounded_contains(answer, GITA_16_7)  # the bug
    scored = score_answer("complete_unit", answer, {"text": GITA_16_7}, language="sa")
    assert scored["contains_reference"] == 1 and scored["outcome"] == "correct"
    assert scored["normalized"] == 0  # equality is unchanged; only containment credits it


@pytest.mark.parametrize(
    "answer, expected",
    [
        ("रसोहमप्सु कौन्तेय", "रसोऽहमप्सु कौन्तेय"),  # single ऽ dropped by the answer
        ("रसोऽहमप्सु कौन्तेय", "रसोहमप्सु कौन्तेय"),  # ऽ added by the answer
        ("योगी परं स्थानमुपैति चाद्यम्", "योगी परं स्थानमुपैति चाऽऽद्यम्"),  # double ऽऽ
    ],
)
def test_avagraha_is_ignored_on_both_sides(answer, expected):
    assert fold_aware_contains(answer, expected)


def test_a_wrong_verse_still_fails():
    assert not fold_aware_contains("न शौचं नापि चाचारो न धर्मः तेषु विद्यते", GITA_16_7)  # one word wrong
    assert not fold_aware_contains("न शौचं नापि चाचारो", GITA_16_7)  # half the verse


def test_a_bare_avagraha_cannot_glue_two_words():
    # A stray ऽ between words leaves the space: सो हम् is still not सोहम्.
    assert not fold_aware_contains("रसो ऽहमप्सु कौन्तेय", "रसोऽहमप्सु कौन्तेय")


def test_an_avagraha_only_reference_never_matches():
    assert not fold_aware_contains("anything at all", "ऽ")


def test_other_scripts_are_untouched():
    # The fold is for a Devanagari reference only. A Latin reference keeps today's rule.
    assert not fold_aware_contains("In the beginning ऽ God", "In the beginning God")


def test_normalize_is_unchanged():
    assert normalize("चाऽऽचारो") == "चाऽऽचारो"


# --- oracle over the committed runs -------------------------------------------------------------

_TEXT_TASKS = ("retrieve_quote", "complete_unit")
_NEVER = "\uffff"  # a code point no reference or answer contains


def _registered() -> set[tuple[str, int, str]]:
    rows = [l.split("\t") for l in MOVERS.read_text(encoding="utf-8").splitlines() if l and not l.startswith("#")]
    registered = {(folder, int(row), qid) for folder, row, qid in rows}
    assert len(registered) == len(rows)
    return registered


def test_committed_cells_move_only_as_registered(monkeypatch):
    score_files = sorted(p for p in RUNS.glob("**/base/**/scores.jsonl") if "archive" not in p.parts)
    if not score_files:
        pytest.skip("runs/ evidence not present")
    moved: set[tuple[str, int, str]] = set()
    for scores in score_files:
        folder = scores.parent.relative_to(RUNS).as_posix()
        answers = [json.loads(l) for l in scores.with_name("answers.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
        for i, row in enumerate(answers):
            if row["task"] not in _TEXT_TASKS:
                continue
            target = row["question"]["expected"]["text"]
            if not any("\u0900" <= c <= "\u097f" for c in target):
                continue  # the fold applies to a Devanagari reference only
            on = fold_aware_contains(row["answer"] or "", target)
            monkeypatch.setattr(score_mod, "_AVAGRAHA", _NEVER)
            off = fold_aware_contains(row["answer"] or "", target)
            monkeypatch.undo()
            if on != off:
                assert off is False and on is True, (folder, i)  # credit-only
                moved.add((folder, i, row["question_id"]))
    assert moved == _registered()
