"""Issue #85: a Masoretic passage is the verse a reader sees, not the OSHB morphology markup.

``build_christian_original.wlc_text`` renders one ``<verse>`` of the pinned morphhb Westminster
Leningrad Codex by METHODOLOGY.md's four rules: the morpheme "/" goes, the pointed Qere replaces the
Ketiv, every other ``<note>`` is apparatus, and the ס/פ paragraph markers go. Maqaf, sof pasuq,
paseq, vowels and cantillation stay. Before the fix the builder only deleted tags, so every slash,
each Ketiv+catchWord+Qere (glued into one token) and the editors' English notes reached the prompts.

The fixtures are verses from the pinned commit, trimmed to the words that carry each rule.
"""
from __future__ import annotations

import importlib
import json
import re
import sys
from pathlib import Path

import pytest

_ITEMS = Path(__file__).resolve().parents[2] / "items" / "for-test"
_MASORETIC = _ITEMS / "christianity" / "native" / "masoretic"
_SLASHED_HEBREW = re.compile(r"[א-ת][֑-ׇ]*/")


@pytest.fixture(scope="module")
def bco():
    review = str(_ITEMS / "review")
    sys.path.insert(0, review)
    try:
        yield importlib.import_module("build_christian_original")
    finally:
        sys.path.remove(review)


# --- the committed files ----------------------------------------------------------------------------

def test_no_masoretic_passage_carries_wlc_markup():
    passages = [
        p for sample in ("population", "familiarity")
        for p in json.loads((_MASORETIC / sample / "passages.json").read_text(encoding="utf-8"))["passages"]
    ]
    assert len(passages) == 23
    for p in passages:
        text = p["text"]["native"]
        assert not re.search(r"[A-Za-z/]", text), p["citation"]  # slashes, "BHS has been…", "KJV:Ps.23.1"
        assert text.endswith("׃"), p["citation"]  # no trailing ס/פ paragraph marker


def test_no_question_file_quotes_a_slashed_hebrew_word():
    # the Masoretic passages are also verify "no" donors in other sets (the Talmud's, and a few more)
    for path in sorted(_ITEMS.rglob("questions.jsonl")):
        assert not _SLASHED_HEBREW.search(path.read_text(encoding="utf-8")), path.relative_to(_ITEMS)


# --- the four rules -------------------------------------------------------------------------------

def test_morpheme_slashes_and_paragraph_markers_go(bco):
    exod_28_43 = """
          <w lemma="c/1961" morph="HC/Vqq3cp" id="02yND">וְ/הָיוּ֩</w>
          <w lemma="5921 a" morph="HR" id="02aYV">עַל</w><seg type="x-maqqef">־</seg><w lemma="175" morph="HNp" id="02ZTZ">אַהֲרֹ֨ן</w>
          <w lemma="b/935" n="1.1.1.0" morph="HR/Vqc/Sp3mp" id="02uhc">בְּ/בֹאָ֣/ם</w>
          <seg type="x-paseq">׀</seg>
          <w lemma="310 a" n="0" morph="HR/Sp3ms" id="02DmQ">אַחֲרָֽי/ו</w><seg type="x-sof-pasuq">׃</seg>
          <seg type="x-samekh">ס</seg>
        """
    assert bco.wlc_text(exod_28_43) == "וְהָיוּ֩ עַל־אַהֲרֹ֨ן בְּבֹאָ֣ם ׀ אַחֲרָֽיו׃"
    pe = '<w lemma="776" morph="HNcbsa" id="x">אָֽרֶץ</w><seg type="x-sof-pasuq">׃</seg>\n<seg type="x-pe">פ</seg>'
    assert bco.wlc_text(pe) == "אָֽרֶץ׃"


def test_the_pointed_qere_replaces_the_ketiv(bco):
    lev_11_21 = (
        '<w lemma="834 a" morph="HTr" id="03BdS">אֲשֶׁר</w><seg type="x-maqqef">־</seg>'
        '<w type="x-ketiv" lemma="3808" morph="HTn" id="037d1">לא</w><note type="variant"><catchWord>לא</catchWord>'
        '<rdg type="x-qere"><w lemma="l" morph="HR/Sp3ms" id="03iGP">ל֤/וֹ</w></rdg></note>\n'
        '          <w lemma="3767" n="0.1.0" morph="HNcbda" id="03LXv">כְרָעַ֨יִם֙</w>'
    )
    assert bco.wlc_text(lev_11_21) == "אֲשֶׁר־ל֤וֹ כְרָעַ֨יִם֙"  # was "אֲשֶׁר־לאלאל֤/וֹ כְרָעַ֨יִם֙"


def test_multi_word_and_unread_or_unwritten_ketiv_qere(bco):
    # 1 Samuel 9:1: a two-word Ketiv joined by a Ketiv-only maqaf, one Qere word
    ketiv_pair = (
        '<w type="x-ketiv" lemma="m/1144" morph="HR/Np" id="09a">מ/בן</w><seg type="x-maqqef" subType="x-ketiv">־</seg>'
        '<w type="x-ketiv" lemma="m/1144" morph="HNp" id="09b">ימין</w><note type="variant"><catchWord>מ/בן־ימין</catchWord>'
        '<rdg type="x-qere"><w lemma="m/1144" morph="HR/Np" id="09c">מִ/בִּנְיָמִ֗ין</w></rdg></note>'
    )
    assert bco.wlc_text(ketiv_pair) == "מִבִּנְיָמִ֗ין"
    # Isaiah 36:12: one Ketiv word, a two-word Qere
    qere_pair = (
        '<w type="x-ketiv" lemma="7890" morph="HNcmpc/Sp3mp" id="23a">שיני/הם</w><note type="variant"><catchWord>שיני/הם</catchWord>'
        '<rdg type="x-qere"><w lemma="4325" morph="HNcmpc" id="23b">מֵימֵ֥י</w> <w lemma="7272" morph="HNcfdc/Sp3mp" id="23c">רַגְלֵי/הֶ֖ם</w></rdg></note>'
    )
    assert bco.wlc_text(qere_pair) == "מֵימֵ֥י רַגְלֵיהֶ֖ם"
    # Judges 20:13: read, not written
    assert bco.wlc_text(
        '<w lemma="14" morph="HVqp3cp" id="07a">אָבוּ֙</w>\n'
        '          <note type="variant"><rdg type="x-qere"><w lemma="1121 a" morph="HNcmpc" id="07b">בְּנֵ֣י</w></rdg></note>'
    ) == "אָבוּ֙ בְּנֵ֣י"
    # Ezekiel 48:16: written, not read
    assert bco.wlc_text(
        '<w lemma="6828" morph="HNcbsa" id="26a">צָפ֗וֹן</w>\n'
        '          <w type="x-ketiv" lemma="2568" morph="HAcbsa" id="26b">חמש</w><note type="variant"><catchWord>חמש</catchWord><rdg type="x-qere"/></note>\n'
        '          <w lemma="2568" morph="HAcbsc" id="26c">חֲמֵ֤שׁ</w>'
    ) == "צָפ֗וֹן חֲמֵ֤שׁ"


def test_every_other_note_is_dropped(bco):
    isaiah_49_7 = (
        '<w lemma="c/7812" n="1" morph="HC/Vvi3mp" id="23tit">וְ/יִֽשְׁתַּחֲוּ֑וּ</w>\n'
        '          <note n="1">BHS has been faithful to the Leningrad Codex where there might be a question of the '
        'validity of the form and we keep the same form as BHS. </note>\n'
        '          <w lemma="4616" morph="HR" id="23hSB">לְמַ֤עַן</w>'
    )
    assert bco.wlc_text(isaiah_49_7) == "וְיִֽשְׁתַּחֲוּ֑וּ לְמַ֤עַן"
    psalms_23_1 = (
        '<w lemma="l/1732" n="1" morph="HR/Np" id="19jhu">לְ/דָוִ֑ד</w>\n'
        '          <note>KJV:Ps.23.1</note>\n'
        '          <w lemma="3068" morph="HNp" id="192fr">יְהוָ֥ה</w>'
    )
    assert bco.wlc_text(psalms_23_1) == "לְדָוִ֑ד יְהוָ֥ה"
    exegesis = '<w lemma="772" morph="ANcbsa" id="27a">אֲרַע</w>\n<note type="exegesis">WLC has this word divided as <rdg>ארעא</rdg>.</note>'
    assert bco.wlc_text(exegesis) == "אֲרַע"


def test_markup_the_rules_do_not_cover_stops_the_build(bco):
    with pytest.raises(SystemExit, match="WLC tagging"):
        bco.wlc_text('<w lemma="413" morph="HR" id="x">אֶל</w> <foot>see BHS</foot>')
    with pytest.raises(SystemExit, match="without a Qere"):
        bco.wlc_text('<w type="x-ketiv" id="x">לא</w><note type="variant"><catchWord>לא</catchWord></note>')
