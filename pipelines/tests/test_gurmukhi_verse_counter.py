"""A Gurmukhi verse counter in an answer is not part of the quotation.

The corpus pankti drops the printed counter (``clean_sggs_line``): ``… ਸਭ ਰਾਤਿ ਰਹਾਉ``. Printed,
the line reads ``… ਸਭ ਰਾਤਿ ॥੧॥ ਰਹਾਉ ॥``. A model that copies it faithfully leaves a ``੧`` inside the
quotation after ``normalize()``, so containment failed and the cell scored incorrect.

``fold_aware_contains`` now also tries the answer with counters between dandas removed, for a
Gurmukhi reference only. It is one more OR, so it only adds credit; ``normalize()`` and the equality
submetrics are unchanged.

The oracle at the bottom re-derives containment for every committed retrieve_quote / complete_unit
cell, fold off and fold on. The cells that move are exactly those registered by identity in
``testdata/gurmukhi_verse_counter_movers.tsv``, and each goes from not contained to contained.
Read-only; the committed ``scores.jsonl`` are not rewritten.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

import sacredbench.score as score_mod
from sacredbench.score import bounded_contains, fold_aware_contains, normalize, score_answer

RUNS = Path(__file__).resolve().parents[2] / "runs"
MOVERS = Path(__file__).parent / "testdata" / "gurmukhi_verse_counter_movers.tsv"

RAHAO = "ਮੈ ਹਰਿ ਹਰਿ ਹਰਿ ਟੇਕ ਸਭ ਦਿਨਸੁ ਸਭ ਰਾਤਿ ਰਹਾਉ"  # Ang 1200:25, as the corpus holds it


def test_the_reported_cell_is_credited():
    # fable, prompt-native, complete_unit 318e714fc6590b9b: right words, printed counter, then more.
    answer = "ਮੈ ਹਰਿ ਹਰਿ ਹਰਿ ਟੇਕ ਸਭ ਦਿਨਸੁ ਸਭ ਰਾਤਿ ॥੧॥ ਰਹਾਉ ॥\nਹਰਿ ਕੀ ਉਪਮਾ ਅਨਿਕ ਅਨਿਕ ਅਨਿਕ ਗੁਨ ਗਾਵਤ ॥"
    assert not bounded_contains(answer, RAHAO)  # the bug: the counter splits the quotation
    scored = score_answer("complete_unit", answer, {"text": RAHAO}, language="pa")
    assert scored["contains_reference"] == 1 and scored["outcome"] == "correct"
    assert scored["normalized"] == 0  # equality is unchanged; only containment credits it


@pytest.mark.parametrize(
    "counter",
    ["॥੧॥", "॥ ੧ ॥", "।।੧।।", "॥1॥", "॥੪॥੯॥੬੦॥", "॥੧॥੨॥"],
)
def test_counter_forms_are_dropped(counter):
    assert fold_aware_contains(f"ਮੈ ਹਰਿ ਹਰਿ ਹਰਿ ਟੇਕ ਸਭ ਦਿਨਸੁ ਸਭ ਰਾਤਿ {counter} ਰਹਾਉ ॥", RAHAO)


def test_a_wrong_pankti_with_counters_still_fails():
    assert not fold_aware_contains("ਮੈ ਹਰਿ ਹਰਿ ਟੇਕ ਸਭ ਦਿਨਸੁ ਸਭ ਰਾਤਿ ॥੧॥ ਰਹਾਉ ॥", RAHAO)  # one ਹਰਿ short
    assert not fold_aware_contains("ਹਰਿ ਕੀ ਉਪਮਾ ਅਨਿਕ ਅਨਿਕ ॥੧॥ ਰਹਾਉ ॥", RAHAO)


def test_a_number_after_a_word_is_not_a_counter():
    # ਮਹਲਾ ੫ names the fifth Guru: the number is a word of the heading and must stay.
    assert score_mod._GURMUKHI_VERSE_COUNTER.sub(" ", "ਗਉੜੀ ਮਹਲਾ ੫ ॥") == "ਗਉੜੀ ਮਹਲਾ ੫ ॥"
    assert fold_aware_contains("ਰਹਾਉ ॥੧॥ ਗਉੜੀ ਮਹਲਾ ੫ ॥", "ਗਉੜੀ ਮਹਲਾ ੫")
    assert not fold_aware_contains("ਗਉੜੀ ਮਹਲਾ ॥ ਸਲੋਕ", "ਗਉੜੀ ਮਹਲਾ ੫")  # the number lost is still a miss


def test_other_scripts_are_untouched():
    # The fold is for a Gurmukhi reference only; a Devanagari or Latin reference keeps today's rule.
    assert not fold_aware_contains("धर्मक्षेत्रे ॥1॥ कुरुक्षेत्रे", "धर्मक्षेत्रे कुरुक्षेत्रे")
    assert not fold_aware_contains("In the beginning ॥1॥ God", "In the beginning God")


def test_normalize_is_unchanged():
    assert normalize("ਸਭ ਰਾਤਿ ॥੧॥ ਰਹਾਉ ॥") == "ਸਭ ਰਾਤਿ ੧ ਰਹਾਉ"


# --- oracle over the committed runs -------------------------------------------------------------

_TEXT_TASKS = ("retrieve_quote", "complete_unit")
_NEVER = re.compile(r"(?!x)x")


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
            if not any("\u0a00" <= c <= "\u0a7f" for c in target):
                continue  # the fold returns before this branch for any other script
            on = fold_aware_contains(row["answer"] or "", target)
            monkeypatch.setattr(score_mod, "_GURMUKHI_VERSE_COUNTER", _NEVER)
            off = fold_aware_contains(row["answer"] or "", target)
            monkeypatch.undo()
            if on != off:
                assert off is False and on is True, (folder, i)  # credit-only
                moved.add((folder, i, row["question_id"]))
    assert moved == _registered()
