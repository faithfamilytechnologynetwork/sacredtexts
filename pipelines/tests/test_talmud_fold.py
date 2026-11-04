"""Issue #149: the Talmud containment fold, from the owner's Talmud normalization guide.

Sefaria's Aramaic Talmud writes ``אף על פי``, ``נכרי``, ``הימנו``, ``וחייבים`` where printings and
models write ``אע״פ``, ``גוי``, ``ממנו``, ``וחייבין``. Before #149 such an answer failed containment
and scored incorrect. ``fold_aware_contains`` now also compares the two under the guide
(``talmud_normalization_terms.tsv``) when the cell's work is the Talmud Bavli and the reference is
Hebrew script. It is one more OR, so it only adds credit; ``normalize()`` and the equality
submetrics are unchanged, and the Masoretic Bible (also Hebrew script) is never folded.

The oracle at the bottom re-derives containment for every committed Talmud retrieve_quote /
complete_unit cell, fold off and fold on. The cells that move are exactly those registered in
``testdata/talmud_fold_movers.tsv``, and each goes incorrect -> correct. Read-only.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import sacredbench.talmud_fold as talmud_fold
from sacredbench.jev import string_settled
from sacredbench.score import fold_aware_contains, normalize, score_answer, score_file
from sacredbench.talmud_fold import TALMUD_WORK, TalmudGuideError, talmud_units

RUNS = Path(__file__).resolve().parents[2] / "runs"
MOVERS = Path(__file__).parent / "testdata" / "talmud_fold_movers.tsv"

# Bava Batra 61a (the corpus line), and argon's facct answer to c27efcf355bf0717.
BAVA_BATRA = "לו מעקה גבוה עשרה טפחים רבי יהודה אומר אם יש לו צורת פתח אף על פי שאינו גבוה עשרה טפחים אינו מכור:"
ARGON = "לו מעקה גבוה עשרה טפחים רבי יהודה אומר אם יש לו צורת פתח אע\"פ שאינו גבוה י' טפחים אינו מכור"


def talmud(answer: str, expected: str) -> bool:
    return fold_aware_contains(answer, expected, work=TALMUD_WORK)


def test_the_reported_cell_is_credited():
    assert not fold_aware_contains(ARGON, BAVA_BATRA)  # the bug
    scored = score_answer("complete_unit", ARGON, {"text": BAVA_BATRA}, language="he", work=TALMUD_WORK)
    assert scored["contains_reference"] == 1 and scored["outcome"] == "correct"
    assert scored["normalized"] == 0  # equality is unchanged; only containment credits it
    unfolded = score_answer("complete_unit", ARGON, {"text": BAVA_BATRA}, language="he")
    assert {k: v for k, v in scored.items() if k not in ("contains_reference", "correct", "outcome")} == {
        k: v for k, v in unfolded.items() if k not in ("contains_reference", "correct", "outcome")
    }


def test_score_file_passes_the_work(tmp_path):
    row = {
        "question_id": "q", "model_id": "m", "task": "complete_unit", "answer": ARGON, "question_set_digest": "d",
        "question": {"expected": {"text": BAVA_BATRA}, "source": {"tradition": ["Judaism"], "work": TALMUD_WORK, "language": "he"}},
    }
    answers = tmp_path / "answers.jsonl"
    answers.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
    score_file(answers, tmp_path / "scores.jsonl")
    assert json.loads((tmp_path / "scores.jsonl").read_text(encoding="utf-8"))["metrics"]["outcome"] == "correct"
    assert string_settled(row)  # jev does not re-judge a cell the string scorer already credits


@pytest.mark.parametrize(
    "a, b",
    [
        ("אע״פ שאינו רשאי", "אף על פי שאינו רשאי"),  # abbreviation
        ("אע\"פ שאינו רשאי", "אף על פי שאינו רשאי"),  # ASCII gershayim
        ("רשב״ג אומר", "רבן שמעון בן גמליאל אומר"),
        ("אמר ר' יוחנן", "אמר רבי יוחנן"),  # ambiguous ר׳: רבי
        ("אמר ר׳ הונא", "אמר רב הונא"),  # ambiguous ר׳: רב
        ("א״ר יוחנן", "אמר רבי יוחנן"),
        ("א״ר הונא", "אמר רב הונא"),
        ("ר״י אומר", "רבי יהודה אומר"),  # ר״י takes the sage the other side names
        ("ר״י אומר", "רבי יוסי אומר"),
        ("ור״ל אמר", "וריש לקיש אמר"),  # a prefixed abbreviation
        ("בר״ה ובניסן", "בראש השנה בניסן"),  # בר״ה is ב + ראש השנה
        ("של גוי", "של נכרי"),  # censorship
        ("של עכו״ם", "של נכרי"),
        ("עובדי כוכבים ומזלות", "גוי"),
        ("לגוי", "לנכרי"),
        ("אמר ה׳", "אמר השם"),  # divine name
        ("אמר יי", "אמר ה׳"),
        ("אלקים", "אלהים"),
        ("ה׳ אמות", "חמש אמות"),  # ה׳ / ד׳ also numerals, read by the other side
        ("ד׳ אמות", "ארבע אמות"),
        ("גבוה י׳ טפחים", "גבוה עשרה טפחים"),  # numerals
        ("כ״א יום", "עשרים ואחד יום"),
        ("כ״א יום", "כל אחד יום"),
        ("י״ב שבטים", "שנים עשר שבטים"),
        ("ט״ו בשבט", "חמשה עשר בשבט"),  # 15 and 16 are written ט״ו / ט״ז
        ("ט״ז יום", "ששה עשר יום"),
        ("תרי ותלתא", "שנים ושלשה"),  # Aramaic number words
        ("שלוש", "שלש"),
        ("משלשה פסוקים", "מג׳ פסוקים"),  # a prefixed number word
        ("בשלשה", "בג׳"),
        ("לעשרה", "לי׳"),
        ("בעשרים ואחד", "בכ״א"),
        ("בשלשה עשר", "בי״ג"),  # a prefixed two-letter numeral
        ("בעשרים ושנים", "בכ״ב"),
        ("בט״ו", "בחמשה עשר"),
        ("ובי״ג", "בשלש עשרה"),
        ("משלשה", "משלושה"),
        ("לאלקים", "לאלהים"),
        ("והמקבל ממנו", "והמקבל הימנו"),  # lexical variants
        ("הללו", "האלו"),
        ("וחייבין עליו", "וחייבים עליו"),  # orthography
        ("הלויים", "הלוים"),
        ("והמשתתף לו", "המשתתף לו"),  # leading ו
        ("לא מכר את היציע", "לא מכר יציע"),  # את ה-
        ("מַתְנִי׳ הַלּוֹקֵחַ", "מתני׳ הלוקח"),  # niqqud
    ],
)
def test_guide_forms_match_in_both_directions(a, b):
    assert talmud(a, b) and talmud(b, a)


@pytest.mark.parametrize(
    "a, b",
    [
        ("רבי יוסי אומר", "רבי יהודה אומר"),  # full names are never collapsed to ר״י
        ("ר״י אומר", "רבי מאיר אומר"),  # ר״מ is רבי מאיר; ר״י is not
        ("ד׳ אמות", "חמש אמות"),
        ("בשלשה", "בארבעה"),
        ("בשלשה", "שלשה"),  # the prefix is part of the word
        ("בעשרים ואחד", "בכ״ב"),
        ("ר׳ יוחנן", "מאתים יוחנן"),  # ר׳ reads as רבי / רב; the abbreviation wins over 200
        ("של גוי", "של ישראל"),
        ("והמקבל ממנו", "והמקבל לו"),
        ("נוהגות", "נוהגין"),  # review only: not applied
        ("לי", "ליה"),  # DO NOT normalize
        ("מין", "צדוקי"),
    ],
)
def test_different_words_still_differ(a, b):
    assert not talmud(a, b)


def test_bar_rosh_hashana_is_not_a_number():
    assert all(not r[0].isdigit() for r in talmud_units("בר״ה")[0])
    assert talmud_units("י״ב") == [frozenset({("12",)})]  # a numeral that is not an abbreviation


def test_accepted_collisions_are_pinned():
    # The owner's rules as written (see talmud_fold's docstring); change them deliberately.
    assert talmud("מים", "מין") and talmud("ימים", "ימין")  # -ים/-ין on words of 3+ letters
    assert talmud("שמנים", "שמונים")  # שמנה is a listed spelling of 8, so שמנים reads as 80
    assert talmud("כותי", "נכרי") and talmud("ארמאי", "גוי")  # notes say "check per passage"


def test_half_a_reference_still_fails():
    assert not talmud("לו מעקה גבוה י׳ טפחים", BAVA_BATRA)


def test_only_the_talmud_is_folded():
    # The Masoretic Bible is Hebrew script too: the work, not the script, turns the fold on.
    verse = "ויאמר אלהים יהי אור ויהי אור"
    assert not fold_aware_contains("ויאמר אלקים יהי אור ויהי אור", verse, work="The Bible")
    assert not fold_aware_contains("ויאמר אלקים יהי אור ויהי אור", verse)
    assert fold_aware_contains("ויאמר אלקים יהי אור ויהי אור", verse, work=TALMUD_WORK)
    # The English Davidson edition shares the work name; a Latin reference keeps today's rule, and
    # an Arabic one keeps the Spec 52 fold.
    for answer, expected in [("R. Yohanan said", "Rabbi Yohanan said"), ("Rabbi Yohanan said so", "Rabbi Yohanan said"),
                             ("الكتاب", "ٱلْكِتَٰبِ"), ("الكتب", "ٱلْكِتَٰبِ")]:
        assert fold_aware_contains(answer, expected, work=TALMUD_WORK) == fold_aware_contains(answer, expected)


def test_normalize_is_unchanged():
    assert normalize("אע״פ שאינו גבוה י׳ טפחים") == "אע פ שאינו גבוה י טפחים"


def test_the_guide_loads_every_row():
    g = talmud_fold.guide()
    assert g.rules == set(talmud_fold._RULE_ROWS.values())
    assert g.readings["א״ר"] == {("אמר", "רבי"), ("אמר", "רב"), ("א״ר",)}
    assert g.readings["ר׳"] == {("רבי",), ("רב",), ("ר׳",)}  # no 200
    assert g.readings["ה׳"] == {("@DIVINE",), ("5",), ("ה׳",)}
    assert len(_rows()) == 182  # the guide is committed whole, review-only rows included


def _rows() -> list[dict]:
    import csv

    with talmud_fold.TERMS_PATH.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def test_an_unknown_row_fails_the_load(tmp_path, monkeypatch):
    bad = tmp_path / "terms.tsv"
    bad.write_text(talmud_fold.TERMS_PATH.read_text(encoding="utf-8") + "xyz\tabc\tmystery\tno\t\t\n", encoding="utf-8")
    monkeypatch.setattr(talmud_fold, "TERMS_PATH", bad)
    talmud_fold.guide.cache_clear()
    try:
        with pytest.raises(TalmudGuideError, match="mystery"):
            talmud_fold.guide()
    finally:
        monkeypatch.undo()
        talmud_fold.guide.cache_clear()


# --- oracle over the committed runs -------------------------------------------------------------

_TEXT_TASKS = ("retrieve_quote", "complete_unit")


def _registered() -> dict[tuple[str, int, str], str]:
    rows = [l.split("\t") for l in MOVERS.read_text(encoding="utf-8").splitlines() if l and not l.startswith("#")]
    registered = {(folder, int(row), qid): task for folder, row, qid, task in rows}
    assert len(registered) == len(rows)
    return registered


def test_committed_cells_move_only_as_registered():
    # Fold off and fold on are both derived from answers.jsonl, never from the committed scores, so
    # the oracle still holds after the sanctioned re-score writes these cells as correct.
    score_files = sorted(RUNS.glob("**/scores.jsonl"))
    if not score_files:
        pytest.skip("runs/ evidence not present")
    moved: dict[tuple[str, int, str], str] = {}
    for scores in score_files:
        if not scores.with_name("answers.jsonl").exists():
            continue
        folder = scores.parent.relative_to(RUNS).as_posix()
        answers = [json.loads(l) for l in scores.with_name("answers.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
        for i, row in enumerate(answers):
            source = row["question"].get("source", {})
            if row["task"] not in _TEXT_TASKS or source.get("work") != TALMUD_WORK:
                continue
            answer, expected = row["answer"] or "", row["question"]["expected"]
            if fold_aware_contains(answer, expected["text"]) == fold_aware_contains(answer, expected["text"], work=TALMUD_WORK):
                continue
            off = score_answer(row["task"], answer, expected, language=source.get("language"))
            on = score_answer(row["task"], answer, expected, language=source.get("language"), work=TALMUD_WORK)
            assert off["outcome"] == "incorrect", (folder, i)
            assert on["outcome"] == "correct" and on["contains_reference"] == 1, (folder, i)  # credit-only
            moved[(folder, i, row["question_id"])] = row["task"]
    assert moved == _registered()
    assert sum(folder.startswith("facct-2026-11-03/") for folder, _, _ in moved) == 33
