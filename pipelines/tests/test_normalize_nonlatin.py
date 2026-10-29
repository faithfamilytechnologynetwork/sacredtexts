"""Arabic/Hebrew normalisation (Spec 8, Phase 1).

`normalize()` must score Qur'an (Arabic) and Talmud (Hebrew/Aramaic) quotes fairly:
combining marks (harakat / niqqud / cantillation), tatweel, and the Qur'anic annotation
symbols are removed and letter variants folded, so a vocalised and an unvocalised spelling
of the same text are equal — in BOTH directions (a vocalised answer vs. an unvocalised
expected, and the reverse). Uthmani dagger alif folds to a full alif (issue #52), so it
matches the Imla'i spelling rather than a skeleton that deletes the vowel. Latin output
must be byte-for-byte unchanged, and the scoring contract (`_SUBMETRICS`, the
`retrieve_quote` headline rule) must not move.

Real fixtures are read from the committed, open-licensed corpora (the QUL Uthmani Qur'an and
the Davidson VOCALISED Aramaic Shevuot file — the latter is deliberately excluded from the
conversion catalogue and is used here only as a mark fixture, never converted into the
corpus). Both files are public-domain / open and already tracked in the repo.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

import pytest

from sacredbench.score import normalize, score_answer, strip_script_marks, token_f1

REPO_ROOT = Path(__file__).resolve().parents[2]
QUL = REPO_ROOT / "texts" / "raw" / "Sunni Islam" / "quran_uthmani_from_qul.json.json"
SHEVUOT_VOCALIZED = (
    REPO_ROOT / "texts" / "raw" / "Judaism" / "Talmud Bavli"
    / "Shevuot - he - William Davidson Edition - Vocalized Aramaic.json"
)

def _strip_combining(s: str) -> str:
    """An INDEPENDENT 'unvocalised' form (stdlib only, not the implementation's block
    logic): NFKD then drop every category-Mn codepoint. This deletes a dagger alif
    rather than rewriting it, so it is NOT the #52 orthography — Arabic equality
    against this helper is no longer the contract. The maqaf is mapped to a space
    to match the implementation's word-boundary rule."""
    s = unicodedata.normalize("NFKD", s).replace("־", " ")
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def _has_surviving_mark(s: str) -> bool:
    """True if any combining mark or Arabic/Hebrew-block editorial code point remains."""
    editorial = frozenset("ـ") | frozenset(chr(c) for c in range(0x06D6, 0x06EE))
    return any(unicodedata.category(c).startswith("M") or c in editorial for c in s)


# --- Arabic ------------------------------------------------------------------


def test_arabic_vocalized_equals_plain_basmala():
    # Real QUL 1:1: the dagger alif is written after a tatweel (مَـٰ), which Imla'i
    # spells as a full alif. Deleting the dagger (it is category Mn) used to drop it.
    vocal = json.loads(QUL.read_text(encoding="utf-8"))["1:1"]["text"]
    assert "ـٰ" in vocal
    plain = "بسم الله الرحمان الرحيم"
    assert normalize(vocal) == plain
    assert token_f1(vocal, plain) == 1.0


def test_arabic_folds_alef_variants_and_tatweel():
    # alef-madda/hamza-above/hamza-below/wasla all fold to a bare alef; tatweel vanishes
    assert normalize("أإآاٱ") == normalize("ااااا")
    assert normalize("مـحـمـد") == normalize("محمد")


def test_uthmani_imlai_orthography_pairs():
    # Issue #52. Targets are spelled out so this fails if the fold is removed
    # (the two sides would still be unequal, and neither would equal the target).
    assert normalize("أَرَءَيْتُمْ") == normalize("أَرَأَيْتُمْ") == "ارايتم"
    assert normalize("أَتَىٰكُمْ") == normalize("أَتَاكُمْ") == "اتاكم"
    # Tatweel, or a fatha that NFKD sorts in front of the dagger (class 30 < 35),
    # is still one alif — not yeh + alif.
    assert normalize("أتىـٰكم") == "اتاكم"
    assert normalize("أَتَىَٰكُمْ") == "اتاكم"
    assert normalize("موسى") == normalize("موسي") == "موسي"


@pytest.mark.parametrize(
    "verse_key,expected",
    [
        # 2:2 has U+06DB plus dagger alif written after tatweel (ٱلْكِتَـٰبُ → الكتاب)
        ("2:2", "ذالك الكتاب لا ريب فيه هدي للمتقين"),
        # 7:206 has the sajdah marker U+06E9, which must disappear rather than split a word
        ("7:206", "ان الذين عند ربك لا يستكبرون عن عبادته ويسبحونه وله يسجدون"),
        # 2:23 has the ىٰ digraph (عَلَىٰ → علا) and hamza seated in شُهَدَاءَكُم
        ("2:23", "وان كنتم في ريب مما نزلنا علا عبدنا فاتوا بسورة من مثله وادعوا شهدااكم من دون الله ان كنتم صادقين"),
    ],
)
def test_real_qul_ayah_marks_removed_without_splitting(verse_key, expected):
    data = json.loads(QUL.read_text(encoding="utf-8"))
    text = data[verse_key]["text"]
    assert _has_surviving_mark(text)  # the raw ayah really carries marks (guards the fixture)
    norm = normalize(text)
    assert not _has_surviving_mark(norm)  # nothing mark-like survives
    # pinned Imla'i-side spelling: a mark turned into a space would add a word, and a
    # deleted dagger alif would drop a letter (الكتب rather than الكتاب)
    assert norm == expected
    assert len(norm.split()) == len(expected.split())


@pytest.mark.parametrize(
    "mark",
    ["ؗ", "ؘ", "ؙ", "ؚ",  # Arabic small high marks (non-QUL Uthmani)
     "ٖ", "ٗ", "٘", "ٟ",  # subscript alef etc. (U+0656–U+065F)
     "ࣰ", "ࣱ", "ࣲ"],            # Arabic Extended-A open tanwin
)
def test_extended_arabic_marks_folded_not_split(mark):
    # marks OUTSIDE the QUL set (a search-on answer may carry them) must still fold, not
    # split the word mid-token — the generic Mn-in-block rule, verified per codepoint.
    base = "الرحمن"
    vocal = base[:3] + mark + base[3:]
    assert normalize(vocal) == normalize(base)
    assert len(normalize(vocal).split()) == 1


# --- Hebrew ------------------------------------------------------------------


def test_real_vocalized_talmud_line_equals_plain():
    data = json.loads(SHEVUOT_VOCALIZED.read_text(encoding="utf-8"))
    line = None
    for section in data["text"]:
        for raw in section or []:
            clean = re.sub(r"<[^>]+>", "", raw).strip()
            if clean and any(0x0591 <= ord(c) <= 0x05C7 for c in clean):
                line = clean
                break
        if line:
            break
    assert line is not None, "expected a vocalised line in the Shevuot fixture"
    assert normalize(line) == normalize(_strip_combining(line))
    assert token_f1(line, _strip_combining(line)) == 1.0


def test_hebrew_maqaf_becomes_word_boundary():
    # the maqaf (U+05BE) joins words like a hyphen; it must become a SPACE so adjacent
    # words don't concatenate (and niqqud is stripped around it)
    assert normalize("עַל־כֵּן") == "על כן"
    assert normalize("עַל־כֵּן").count(" ") == 1


# --- asymmetric direction (the contrast-preserving property) -----------------


def test_retrieve_quote_scores_equal_regardless_of_vocalisation_direction():
    # Qur'an: expected is vocalised QUL (dagger alif after tatweel); the model answers
    # in the Imla'i spelling that writes that vowel as a full alif.
    ayah_vocal = json.loads(QUL.read_text(encoding="utf-8"))["1:2"]["text"]
    ayah_plain = "الحمد لله رب العالمين"
    r = score_answer("retrieve_quote", ayah_plain, {"text": ayah_vocal})
    assert r["normalized"] == 1 and r["correct"] == 1 and r["token_f1"] == 1.0
    # Talmud: expected is unvocalised (catalogued Aramaic), a search-on model answers in
    # VOCALISED text -> must NOT be penalised (this is the direction that would otherwise
    # invert the web-search contrast)
    data = json.loads(SHEVUOT_VOCALIZED.read_text(encoding="utf-8"))
    vocal = next(
        re.sub(r"<[^>]+>", "", raw).strip()
        for section in data["text"] for raw in (section or [])
        if re.sub(r"<[^>]+>", "", raw).strip()
        and any(0x0591 <= ord(c) <= 0x05C7 for c in re.sub(r"<[^>]+>", "", raw))
    )
    plain = _strip_combining(vocal)
    r = score_answer("retrieve_quote", vocal, {"text": plain})
    assert r["normalized"] == 1 and r["correct"] == 1 and r["token_f1"] == 1.0


# --- Latin invariance --------------------------------------------------------


@pytest.mark.parametrize(
    "text,expected",
    [
        ("The keeper planted twelve trees.", "the keeper planted twelve trees"),
        ("“Love one’s neighbour!”", "love one s neighbour"),
        ("A  B\n C", "a b c"),
        # pre-existing behaviour: NFKD splits Latin diacritics at the punctuation pass;
        # the Arabic/Hebrew change must NOT alter this (strip_script_marks is a no-op here)
        ("naïve café résumé", "nai ve cafe re sume"),
    ],
)
def test_latin_output_unchanged(text, expected):
    assert normalize(text) == expected


def test_strip_script_marks_is_a_noop_on_latin():
    for s in ["Hello, world!", "café", "coöperate", "John 3:16"]:
        assert strip_script_marks(unicodedata.normalize("NFKD", s)) == unicodedata.normalize("NFKD", s)
