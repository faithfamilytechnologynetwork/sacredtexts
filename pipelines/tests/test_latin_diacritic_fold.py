"""Issue #94: an English edition's transliteration marks (Allāh, Islām, Pârtha) do not fail a
retrieval that writes the plain English spelling.

The fold is scoring-only and English-only (``source.language == "en"``). ``normalize()`` keeps
the marks, so generation, the question-set digest and the audit do not change. Pali keeps
them in the headline too: there the macron is the orthography (dhamma ≠ dhammā, issue #50).

The oracle at the bottom re-scores the committed 2026-11-02 English answers. The only cells
whose committed (pre-#94) scores disagree with the #94 scorer are the ones registered in
``testdata/latin_fold_movers.tsv``, and each one gains credit and loses nothing.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from sacredbench.score import fold_aware_contains, fold_latin_marks, normalize, score_answer, token_f1

REPO_ROOT = Path(__file__).resolve().parents[2]
MOVERS = Path(__file__).parent / "testdata" / "latin_fold_movers.tsv"

SAHEEH_REF = "Allāh is the Light of the heavens and the earth."


def _rq(answer: str, reference: str, language: "str | None" = "en") -> dict:
    return score_answer("retrieve_quote", answer, {"text": reference}, language=language)


def test_plain_english_spelling_is_credited():
    exact = _rq("Allah is the Light of the heavens and the earth.", SAHEEH_REF)
    assert exact["normalized"] == 1 and exact["contains_reference"] == 1
    assert exact["outcome"] == "correct"
    wrapped = _rq('Qur\'an 24:35 (Saheeh International): "Allah is the Light of the heavens and the earth."', SAHEEH_REF)
    assert wrapped["normalized"] == 0 and wrapped["contains_reference"] == 1
    assert wrapped["outcome"] == "correct"


def test_the_fold_is_symmetric():
    # Besant prints both "Pârtha" and "Partha"; an answer may carry marks the reference lacks.
    scored = _rq("Verily the Mahâtmâs, O Pârtha, worship Me.", "Verily the Mahâtmâs, O Partha, worship Me.")
    assert scored["normalized"] == 1 and scored["outcome"] == "correct"


def test_only_english_cells_fold():
    answer = "Allah is the Light of the heavens and the earth."
    for language in (None, "ar", "la"):
        assert _rq(answer, SAHEEH_REF, language)["correct"] == 0
    # #50's headline rule stands for Pali: the right letters with the wrong vowel length are wrong.
    assert _rq("yo ca vassasataṃ jīve dhamma", "yo ca vassasataṃ jīve dhammā", "pi")["correct"] == 0


def test_a_different_word_is_still_wrong():
    # The fold removes marks; word boundaries still hold.
    assert _rq("Allahumma, the Light of the heavens and the earth.", "Allāh")["correct"] == 0
    assert _rq("Allah is the Light of the heavens.", SAHEEH_REF)["correct"] == 0


def test_shared_normalize_and_diagnostics_do_not_change():
    assert normalize("Allāh") == "allāh" != normalize("Allah")
    assert token_f1("Allah", "Allāh") == 0
    assert not fold_aware_contains("Allah", "Allāh")  # the default path keeps the marks
    assert fold_aware_contains("Allah", "Allāh", fold_latin=True)
    # Indic vowel signs and Arabic letters pass through the fold untouched.
    for text in ("कर्ता", "ਕਰਤੀ", "بِسْمِ ٱللَّهِ"):
        assert fold_latin_marks(normalize(text)) == normalize(text)


def test_cite_passage_does_not_fold():
    scored = score_answer("cite_passage", "Sūrat al-Baqarah 2:255", {"citation": "Surat al-Baqarah 2:255"}, language="en")
    assert scored["correct"] == 0


# --- oracle over the committed 2026-11-02 run ------------------------------------------------

# The registered upgrade: only these keys change, and the cell becomes correct.
_UPGRADE_KEYS = {"normalized", "contains_reference", "correct", "outcome"}


def _registered() -> dict[tuple[str, str, str], str]:
    rows = [l.split("\t") for l in MOVERS.read_text(encoding="utf-8").splitlines() if l and not l.startswith("#")]
    return {(folder, task, qid): outcome for folder, task, qid, outcome in rows}


def test_registered_mover_counts():
    by_kind: dict[tuple[str, str], int] = {}
    for (folder, _, _), outcome in _registered().items():
        tradition = folder.split("/")[2]
        by_kind[(tradition, outcome)] = by_kind.get((tradition, outcome), 0) + 1
    assert by_kind == {("islam", "incorrect"): 151, ("hinduism", "incorrect"): 15, ("hinduism", "refused"): 1}


def test_committed_english_cells_move_only_as_registered(completion_head_movers):
    registered = _registered()
    score_files = sorted((REPO_ROOT / "runs").glob("*/base/**/scores.jsonl"))
    if not score_files:
        pytest.skip("runs/ evidence not present")
    seen: set[tuple[str, str, str]] = set()
    for scores in score_files:
        folder = scores.parent.relative_to(REPO_ROOT / "runs").as_posix()
        answers = [json.loads(l) for l in scores.with_name("answers.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
        committed = [json.loads(l) for l in scores.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(answers) == len(committed), folder  # score_file keeps row order, so pair by position
        for i, (row, old) in enumerate(zip(answers, committed)):
            language = row["question"]["source"].get("language")
            if row["task"] not in ("retrieve_quote", "complete_unit") or language != "en":
                continue
            new = score_answer(row["task"], row["answer"], row["question"]["expected"], language=language)
            key = (folder, row["task"], row["question_id"])
            if (folder, i, row["question_id"]) in completion_head_movers and new != old["metrics"]:
                # issue #150, not yet re-scored: the completion head credits it, nothing else moves
                changed = {k for k in new if new[k] != old["metrics"].get(k)}
                assert changed == {"contains_reference", "correct", "outcome"}, (key, changed)
                assert (old["metrics"]["outcome"], new["outcome"]) == ("incorrect", "correct"), key
                continue
            if key not in registered:
                assert new == old["metrics"], f"{key} moved but is not registered"
                continue
            seen.add(key)
            assert new["outcome"] == "correct", key
            if new != old["metrics"]:  # not yet re-scored under #94
                changed = {k for k in new.keys() | old["metrics"].keys() if new.get(k) != old["metrics"].get(k)}
                assert changed <= _UPGRADE_KEYS, (key, changed)
                assert old["metrics"]["outcome"] == registered[key], key
    assert seen == set(registered), f"registered cells missing from runs/: {sorted(set(registered) - seen)[:5]}"
