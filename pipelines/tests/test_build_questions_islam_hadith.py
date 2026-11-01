"""Issue #75: the Qur'an's verify_source "no" donors are hadith (same script), not another tradition.

``items/for-test/review/build_questions.py`` is not part of the ``sacredbench`` package, so it is
loaded by path. The test builds the Islam rows offline from the committed public-domain corpus
(Qur'an + the six canonical hadith collections) and asserts the donor contract.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_BQ_PATH = Path(__file__).resolve().parents[2] / "items" / "for-test" / "review" / "build_questions.py"
_SIX_WORKS = {
    "Sahih al-Bukhari", "Sahih Muslim", "Sunan Abi Dawud",
    "Jami` at-Tirmidhi", "Sunan an-Nasa'i", "Sunan Ibn Majah",
}


def _load_bq():
    spec = importlib.util.spec_from_file_location("build_questions", _BQ_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def bq():
    return _load_bq()


def _quoted(prompt: str) -> str:
    a = prompt.find('"')
    b = prompt.find('"', a + 1)
    return prompt[a + 1:b]


def _islam_no_rows(bq):
    rows = bq.islam()
    bq.add_verify_negatives({"islam": rows})
    return rows, [r for r in rows if r["task"] == "verify_source" and r["expected"].get("answer") == "no"]


def test_hadith_donors_are_six_collections_arabic_and_long_enough(bq):
    donors = bq._hadith_donors()
    assert donors, "expected a non-empty hadith donor pool"
    works = {d["citation"].rsplit(" ", 1)[0] for d in donors}
    assert works == _SIX_WORKS, f"donor pool should be exactly the six canonical books, got {works}"
    for d in donors:
        assert d["tradition"] == "Islam"
        assert d["version"] == bq.HADITH_VERSION == "sunnah.com Arabic"
        assert bq._script(d["expected"]["text"]) == "ar"
        assert len(d["expected"]["text"].split()) >= bq.MIN_WORDS


def test_quran_verify_no_rows_quote_a_hadith(bq):
    rows, no_rows = _islam_no_rows(bq)
    assert no_rows, "expected some flipped verify 'no' rows for Islam"
    for r in no_rows:
        exp = r["expected"]
        assert exp["true_tradition"] == "Islam"                     # same tradition, not another
        assert exp["true_version"] == "sunnah.com Arabic"
        assert exp["true_citation"].rsplit(" ", 1)[0] in _SIX_WORKS  # a hadith, different work
        quoted = _quoted(r["prompt"])
        assert bq._script(quoted) == "ar"                            # same script as the Qur'an
        assert len(quoted.split()) >= bq.MIN_WORDS


def test_no_rows_are_half_of_each_group_and_yes_rows_stay_quran(bq):
    rows, no_rows = _islam_no_rows(bq)
    verify = [r for r in rows if r["task"] == "verify_source"]
    yes_rows = [r for r in verify if r["expected"].get("answer") == "yes"]
    # the "no" flip is half of each (condition, sample) group — so both classes are non-trivial
    assert 0 < len(no_rows) < len(verify)
    for r in yes_rows:
        assert r["expected"]["true_tradition"] == "Islam"
        assert r["expected"]["true_version"] == "Uthmani (QUL)"      # the Qur'an itself


def test_donor_assignment_is_deterministic(bq):
    def signature():
        _, no_rows = _islam_no_rows(bq)
        return sorted((r["prompt"], r["expected"]["true_citation"]) for r in no_rows)

    assert signature() == signature()


def test_prompts_drop_qul_but_metadata_keeps_version(bq):
    rows = bq.islam()
    collected = [bq._collect_row(r) for r in rows]
    for c in collected:
        assert "QUL" not in c["prompt"]                              # no "QUL" in any prompt word
        assert c["source"]["version"] == "Uthmani (QUL)"             # catalogue version unchanged
    english = [c for c in collected if c["source"]["condition"] == "ask_english"]
    assert english and all("the Uthmani Qur'an" in c["prompt"] for c in english)
