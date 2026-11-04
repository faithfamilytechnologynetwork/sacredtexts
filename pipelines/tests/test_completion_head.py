"""A complete_unit answer is scored against the first ten words of the continuation (#150).

The continuation is the rest of the unit. A verse leaves 5–14 words; a prose unit can leave more
than a hundred (an encyclical paragraph, a Talmud segment, a Saheeh verse). A model that continues
correctly and then stops at a natural pause, or drifts, was scored incorrect only because the unit
runs on past a point it cannot know.

``score_answer`` now also counts ``contains_reference`` as met when the answer holds the first ten
words (``completion_head``). A word is a whitespace token of ``normalize()``, so the count is the
same in every script. The full continuation still counts, so this only adds credit. ``exact``,
``normalized`` and the token-F1 overlaps keep the full continuation. ``retrieve_quote`` is unchanged.

The oracle at the bottom re-derives the headline of every committed complete_unit cell with and
without the cut. The cells that move are exactly those registered by identity in
``testdata/completion_head_movers.tsv``, and each goes from incorrect to correct. Read-only; the
committed ``scores.jsonl`` are not rewritten.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pytest

import sacredbench.score as score_mod
from sacredbench.score import completion_head, normalize, score_answer

RUNS = Path(__file__).resolve().parents[2] / "runs"

# Fides et Ratio 62, the remainder after "This ordering of studies" (41 words).
FIDES_62 = (
    "influenced, promoted and enabled much of the development of modern philosophy, albeit "
    "indirectly. One telling example of this is the influence of the Disputationes Metaphysicae of "
    "Francisco Suárez, which found its way even into the Lutheran universities of Germany."
)
FIDES_62_HEAD = "influenced, promoted and enabled much of the development of modern"


def _complete(answer: str, text: str, language: str = "en") -> dict:
    return score_answer("complete_unit", answer, {"text": text}, language=language)


def test_the_head_is_the_first_ten_words():
    assert completion_head(FIDES_62) == FIDES_62_HEAD
    assert normalize(completion_head(FIDES_62)).split() == normalize(FIDES_62).split()[:10]


def test_a_short_continuation_is_unchanged():
    text = "and the earth was without form, and void"
    assert completion_head(text) == text
    assert completion_head(FIDES_62_HEAD) == FIDES_62_HEAD  # exactly ten words


def test_ten_correct_words_then_a_drift_is_correct():
    answer = FIDES_62_HEAD + " thought, and it shaped the universities of Europe for centuries."
    scored = _complete(answer, FIDES_62)
    assert scored["contains_reference"] == 1 and scored["outcome"] == "correct"


def test_nine_correct_words_then_a_drift_is_still_incorrect():
    answer = "influenced, promoted and enabled much of the development of Catholic theology."
    scored = _complete(answer, FIDES_62)
    assert scored["contains_reference"] == 0 and scored["outcome"] == "incorrect"


def test_the_full_continuation_is_still_correct():
    scored = _complete(FIDES_62, FIDES_62)
    assert scored["exact"] == scored["normalized"] == scored["contains_reference"] == 1
    assert scored["outcome"] == "correct"


def test_equality_and_overlap_keep_the_full_continuation():
    scored = _complete(FIDES_62_HEAD + ".", FIDES_62)
    assert scored["outcome"] == "correct"
    assert scored["exact"] == 0 and scored["normalized"] == 0
    assert scored["token_f1"] < 0.5  # ten of 41 words: the near-miss overlap is unchanged


def test_retrieve_quote_is_untouched():
    scored = score_answer("retrieve_quote", FIDES_62_HEAD, {"text": FIDES_62}, language="en")
    assert scored["contains_reference"] == 0 and scored["outcome"] == "incorrect"


def test_a_possessive_counts_as_normalize_counts_it():
    # normalize() splits "Lord's" into two words, so the cut falls one raw word earlier.
    text = "for the Lord's sake and for the sake of all who love him in truth"
    assert completion_head(text) == "for the Lord's sake and for the sake of"


@pytest.mark.parametrize(
    "text, head, language",
    [
        # Hebrew: the maqaf joins two words that normalize() splits (Genesis 1:2).
        (
            "וְהָאָרֶץ הָיְתָה תֹהוּ וָבֹהוּ וְחֹשֶׁךְ עַל־פְּנֵי תְהוֹם וְרוּחַ אֱלֹהִים מְרַחֶפֶת עַל־פְּנֵי הַמָּיִם׃",
            "וְהָאָרֶץ הָיְתָה תֹהוּ וָבֹהוּ וְחֹשֶׁךְ עַל־פְּנֵי תְהוֹם וְרוּחַ אֱלֹהִים",
            "he",
        ),
        # Gurmukhi: the double danda is not a word, and the vowel signs stay on their letters.
        (
            "ਸੋਚੈ ਸੋਚਿ ਨ ਹੋਵਈ ਜੇ ਸੋਚੀ ਲਖ ਵਾਰ ॥ ਚੁਪੈ ਚੁਪ ਨ ਹੋਵਈ ਜੇ ਲਾਇ ਰਹਾ ਲਿਵ ਤਾਰ ॥",
            "ਸੋਚੈ ਸੋਚਿ ਨ ਹੋਵਈ ਜੇ ਸੋਚੀ ਲਖ ਵਾਰ ॥ ਚੁਪੈ ਚੁਪ",
            "pa",
        ),
        # Devanagari: virama, anusvara and visarga are part of the word (Bhagavad Gita 2:20).
        (
            "न जायते म्रियते वा कदाचिन् नायं भूत्वा भविता वा न भूयः । अजो नित्यः शाश्वतोऽयं पुराणो",
            "न जायते म्रियते वा कदाचिन् नायं भूत्वा भविता वा न",
            "sa",
        ),
    ],
)
def test_words_are_counted_the_same_in_every_script(text, head, language):
    assert completion_head(text) == head
    assert normalize(head).split() == normalize(text).split()[:10]
    scored = _complete(head + " " + "क ख ग", text, language)  # ten right words, then a drift
    assert scored["outcome"] == "correct"


def test_the_arabic_head_keeps_its_marks_for_the_orthography_fold():
    # Al-Baqarah 2:2–3 in Uthmani. The head is cut from the raw text, so the dagger-alif in
    # ٱلْكِتَٰبُ is still there and an Imla'i answer (الكتاب) is credited by the Spec 52 fold.
    text = "ذَٰلِكَ ٱلْكِتَٰبُ لَا رَيْبَ فِيهِ هُدًى لِّلْمُتَّقِينَ ٱلَّذِينَ يُؤْمِنُونَ بِٱلْغَيْبِ وَيُقِيمُونَ ٱلصَّلَوٰةَ"
    assert completion_head(text) == "ذَٰلِكَ ٱلْكِتَٰبُ لَا رَيْبَ فِيهِ هُدًى لِّلْمُتَّقِينَ ٱلَّذِينَ يُؤْمِنُونَ بِٱلْغَيْبِ"
    answer = "ذلك الكتاب لا ريب فيه هدى للمتقين الذين يؤمنون بالغيب ويؤتون الزكاة"
    scored = _complete(answer, text, "ar")
    assert scored["contains_reference"] == 1 and scored["outcome"] == "correct"


# --- oracle over the committed runs -------------------------------------------------------------


def test_registered_mover_counts(completion_head_movers):
    by_run = Counter(
        folder.split("/")[0] if not folder.startswith("archive/") else "/".join(folder.split("/")[:2])
        for folder, _, _ in completion_head_movers
    )
    facct = by_run.pop("facct-2026-11-03")
    archive = {k: by_run.pop(k) for k in list(by_run) if k.startswith("archive/")}
    assert (facct, sum(by_run.values()), archive) == (
        178, 205, {"archive/original-2026-10-21": 18, "archive/exp-provider-native-search-2026-10-29": 3},
    )


def test_committed_cells_move_only_as_registered(monkeypatch, completion_head_movers):
    score_files = sorted(RUNS.glob("**/scores.jsonl"))
    if not score_files:
        pytest.skip("runs/ evidence not present")
    moved: set[tuple[str, int, str]] = set()
    for scores in score_files:
        folder = scores.parent.relative_to(RUNS).as_posix()
        answers = [json.loads(l) for l in scores.with_name("answers.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
        committed = [json.loads(l) for l in scores.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(answers) == len(committed), folder  # score_file keeps row order, so pair by position
        for i, (row, old) in enumerate(zip(answers, committed)):
            if row["task"] != "complete_unit":
                continue
            assert row["question_id"] == old["question_id"], folder
            expected = row["question"]["expected"]
            if completion_head(expected["text"]) == expected["text"]:
                continue  # ten words or fewer: the cell cannot move
            args = ("complete_unit", row["answer"] or "", expected)
            language = row["question"].get("source", {}).get("language")
            post = score_answer(*args, language=language)
            with monkeypatch.context() as m:
                m.setattr(score_mod, "completion_head", lambda text: text)
                pre = score_answer(*args, language=language)
            if pre != post:
                assert (pre["outcome"], post["outcome"]) == ("incorrect", "correct"), (folder, i)
                changed = {k for k in pre if pre[k] != post[k]}
                assert changed == {"contains_reference", "correct", "outcome"}, (folder, i, changed)
                moved.add((folder, i, row["question_id"]))
    assert moved == completion_head_movers
