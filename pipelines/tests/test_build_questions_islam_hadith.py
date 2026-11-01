"""Issue #75 / PR #78: the Qur'an's verify_source "no" items quote a hadith matn in the same script.

``items/for-test/review/build_questions.py`` and ``build_review.py`` are not part of the ``sacredbench``
package, so they are loaded by path. Everything here is offline: the Qur'an, the six canonical hadith
collections, the Talmud and the SGGS are committed public-domain/open raw data.

What is pinned:
- the donor set is the six canonical collections, read from ``texts/raw/Sunni Islam/source.yaml``;
- a donor is a saying: the one quoted span that opens right after a salawat (owner-approved
  matn-only, quote-bounded) — never the isnad, never a narrator's remark or chain after it;
- round-3 guards: a donor never opens with a chain or reported clause (حَدَّثَنَا … عَنْ, وَعَنْ, أَنَّ),
  is never itself a bare verdict, never carries God's speech (hadith qudsi) or a salawat;
- no donor shares Qur'an wording (owner-raised) — checked over every committed Islam "no" row;
- the gate is the quoted passage's script, not the tradition, and each Arabic row's donor is seeded
  by that row alone, so no other tradition can move it;
- the committed Islam question files are exactly what the generator builds, and the Islam review
  page prints the same prompt wording the question files use;
- the PR-body claims about the samples (population ∩ familiarity = ∅, population verses ≥16 words).
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
import unicodedata
from pathlib import Path

import pytest

from sacredbench.score import parse_yes_no

_REPO = Path(__file__).resolve().parents[2]
_REVIEW = _REPO / "items" / "for-test" / "review"
_ISLAM = _REPO / "items" / "for-test" / "islam"
_SIX_WORKS = (
    "Sahih al-Bukhari", "Sahih Muslim", "Sunan Abi Dawud",
    "Jami` at-Tirmidhi", "Sunan an-Nasa'i", "Sunan Ibn Majah",
)


def _nfd(text: str) -> str:
    """Canonical mark order: sunnah.com writes shadda+fatha in either order."""
    return unicodedata.normalize("NFD", text)


# narrator-chain / reported-clause openers (architect, round 3: عَنْ, وَعَنْ, أَنَّ too), by letters with
# hamza kept, so أَنَّ ("that …") is caught and إِنَّ ("indeed") is not
_ISNAD = frozenset({"حدثنا", "حدثني", "أخبرنا", "أخبرني", "اخبرنا", "اخبرني", "أنبأنا", "عن", "وعن", "أن"})


def _first_word_letters(text: str) -> str:
    word = unicodedata.normalize("NFC", text.split()[0])
    return "".join(c for c in word if unicodedata.category(c).startswith("L"))


def _opens_with_isnad(text: str) -> bool:
    return _first_word_letters(text) in _ISNAD


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _REVIEW / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def bq():
    return _load("build_questions")


@pytest.fixture(scope="module")
def br():
    # build_review imports build_questions by name, as it does when run as a script
    sys.path.insert(0, str(_REVIEW))
    try:
        yield _load("build_review")
    finally:
        sys.path.remove(str(_REVIEW))


def _islam_built(bq) -> list[dict]:
    rows = bq.islam()
    bq.add_verify_negatives({"islam": rows})
    return rows


def _no_rows(rows: list[dict]) -> list[dict]:
    return [r for r in rows if r["task"] == "verify_source" and r["expected"].get("answer") == "no"]


def _committed_islam_rows() -> list[dict]:
    rows = []
    for path in sorted(_ISLAM.glob("native/*/prompt-*/questions.jsonl")):
        rows.extend(json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    assert rows, "expected committed Islam question files"
    return rows


# --- donor source: the six collections, from source.yaml ------------------------------------------

def test_hadith_collections_are_the_six_arabic_targets_in_source_yaml(bq):
    targets = bq.hadith_collections()
    assert tuple(t.work for t in targets) == _SIX_WORKS == bq.KUTUB_AL_SITTAH
    for t in targets:
        assert t.converter == "hadith_sunnah" and t.language == "ar"
        assert t.version == "sunnah.com Arabic"
        assert (bq.RAW / "Sunni Islam" / t.payload).is_file()


# --- sayings only: the quoted span after a salawat (owner, round 2) -------------------------------

_MATN = " ".join(["كلمة"] * 20)
_SAL = "صلى الله عليه وسلم"
_Q = '\u200f"\u200f'  # sunnah.com's quotation mark, wrapped in right-to-left marks


@pytest.mark.parametrize("text,expected", [
    # the quoted span after a salawat and a speech verb
    (f"حَدَّثَنَا فُلَانٌ عَنِ النَّبِيِّ {_SAL} قَالَ {_Q} {_MATN} {_Q}", _MATN),
    (f"أَخْبَرَنَا فُلَانٌ عَنِ النَّبِيِّ {_SAL} أَنَّهُ قَالَ: {_Q} {_MATN} {_Q}", _MATN),
    (f"سَمِعْتُ رَسُولَ اللَّهِ {_SAL}، يَقُولُ : {_Q}\n{_MATN} {_Q}", _MATN),
    (f"أَتَيْتُ النَّبِيَّ {_SAL} فَقَالَ {_Q} {_MATN} {_Q}", _MATN),
    # ... or with no verb between: قَالَ رَسُولُ اللَّهِ ﷺ "…"
    (f"قَالَ رَسُولُ اللَّهِ {_SAL} {_Q} {_MATN} {_Q}", _MATN),
    # vowelled, line-broken and ligature (ﷺ) salawat are all the salawat
    (f"عَنْ فُلَانٍ أَنَّ رَسُولَ اللَّهِ صَلَّى اللَّهُ عَلَيْهِ وَسَلَّمَ قَالَ {_Q} {_MATN} {_Q}", _MATN),
    (f"عَنْ فُلَانٍ أَنَّ رَسُولَ اللَّهِ صلى\n الله عليه وسلم قَالَ {_Q} {_MATN} {_Q}", _MATN),
    (f"عَنِ النَّبِيِّ \ufdfa قَالَ {_Q} {_MATN} {_Q}", _MATN),
    # the span ends at its closing mark: commentary, a remark or a second chain after it is not quoted
    (f"عَنِ النَّبِيِّ {_SAL} قَالَ {_Q} {_MATN} {_Q}\u200f.\u200f قَالَ أَبُو عِيسَى هَذَا حَدِيثٌ حَسَنٌ", _MATN),
    (f"عَنِ النَّبِيِّ {_SAL} قَالَ {_Q} {_MATN} {_Q} وَحَدَّثَنَا فُلَانٌ عَنْ فُلَانٍ بِمِثْلِهِ", _MATN),
    # the FIRST salawat that opens a quotation: a salawat inside the chain is skipped
    (f"حَدَّثَنَا فُلَانٌ عَنِ النَّبِيِّ {_SAL} وَحَدَّثَنِي فُلَانٌ عَنِ النَّبِيِّ {_SAL} قَالَ {_Q} {_MATN} {_Q}", _MATN),
    # no quotation right after a salawat: an unquoted saying, narration, her words, no salawat at all
    (f"عَنِ النَّبِيِّ {_SAL} قَالَ {_MATN}", None),
    (f"كَانَ النَّبِيُّ {_SAL} إِذَا {_MATN}", None),
    (f"دَخَلَ عَلَيَّ النَّبِيُّ {_SAL} قَالَتْ {_Q} {_MATN} {_Q}", None),
    (f"حَدَّثَنَا فُلَانٌ قَالَ {_Q} {_MATN} {_Q}", None),
    # an unclosed quotation, a span under MIN_WORDS words, or a chain inside the quotation
    (f"عَنِ النَّبِيِّ {_SAL} قَالَ {_Q} {_MATN}", None),
    (f"عَنِ النَّبِيِّ {_SAL} قَالَ {_Q} كَلِمَةٌ قَصِيرَةٌ {_Q} {_MATN}", None),
    (f"عَنِ النَّبِيِّ {_SAL} قَالَ {_Q} حَدَّثَنَا {_MATN} {_Q}", None),
    # round 3 guards — a reported clause opens the span: عَنْ / وَعَنْ / أَنَّ (إِنَّ is a normal opening)
    (f"عَنِ النَّبِيِّ {_SAL} قَالَ {_Q} عَنْ {_MATN} {_Q}", None),
    (f"عَنِ النَّبِيِّ {_SAL} قَالَ {_Q} وَعَنْ {_MATN} {_Q}", None),
    (f"عَنِ النَّبِيِّ {_SAL} قَالَ {_Q} أَنَّ {_MATN} {_Q}", None),
    (f"عَنِ النَّبِيِّ {_SAL} قَالَ {_Q} إِنَّ {_MATN} {_Q}", f"إِنَّ {_MATN}"),
    # ... the span is itself a bare verdict ("لاَ، …"); a negation (لاَ تَبِيعُوا) is a normal opening
    (f"عَنِ النَّبِيِّ {_SAL} قَالَ {_Q} لاَ، {_MATN} {_Q}", None),
    (f"عَنِ النَّبِيِّ {_SAL} قَالَ {_Q} نَعَمْ . {_MATN} {_Q}", None),
    (f"عَنِ النَّبِيِّ {_SAL} قَالَ {_Q} لاَ تَبِيعُوا {_MATN} {_Q}", f"لاَ تَبِيعُوا {_MATN}"),
    # ... God's speech (hadith qudsi, or an ayah framed as قَالَ اللَّهُ); "اللَّهُمَّ" is a prayer, not that
    (f"عَنِ النَّبِيِّ {_SAL} قَالَ {_Q} قَالَ اللَّهُ تَعَالَى {_MATN} {_Q}", None),
    (f"عَنِ النَّبِيِّ {_SAL} قَالَ {_Q} {_MATN} يَقُولُ اللَّهُ عَزَّ وَجَلَّ {_Q}", None),
    (f"عَنِ النَّبِيِّ {_SAL} قَالَ {_Q} إِنَّ اللَّهَ عَزَّ وَجَلَّ يَقُولُ {_MATN} {_Q}", None),
    (f"عَنِ النَّبِيِّ {_SAL} قَالَ {_Q} إِنَّ اللَّهَ قَالَ {_MATN} {_Q}", None),
    (f"عَنِ النَّبِيِّ {_SAL} قَالَ {_Q} {_MATN} قَالَ رَبُّكُمْ {_Q}", None),
    (f"عَنِ النَّبِيِّ {_SAL} قَالَ {_Q} قُولُوا اللَّهُمَّ {_MATN} {_Q}", f"قُولُوا اللَّهُمَّ {_MATN}"),
    (f"عَنِ النَّبِيِّ {_SAL} قَالَ {_Q} إِنَّ اللَّهَ يُحِبُّ {_MATN} {_Q}", f"إِنَّ اللَّهَ يُحِبُّ {_MATN}"),
    # ... a salawat inside the span: the Qur'an never has one
    (f"عَنِ النَّبِيِّ {_SAL} قَالَ {_Q} {_MATN} لاَ يَحِلُّ لآلِ مُحَمَّدٍ {_SAL} {_Q}", None),
])
def test_hadith_matn_is_the_quoted_saying_after_a_salawat(bq, text, expected):
    assert bq.hadith_matn(text) == expected


def test_real_hadith_matn_bukhari_1(bq):
    target = bq.hadith_collections()[0]
    data = json.loads((bq.RAW / "Sunni Islam" / target.payload).read_text(encoding="utf-8"))
    first = next(h for h in data["hadiths"] if h["idInBook"] == 1)["arabic"]
    matn = bq.hadith_matn(first)
    assert _opens_with_isnad(first)                              # the hadith opens with its isnad ...
    assert _nfd("إِنَّمَا الْأَعْمَالُ بِالنِّيَّاتِ") in _nfd(matn)          # ... the matn is the saying
    assert _nfd("حَدَّثَنَا") not in _nfd(matn) and not _nfd(matn).startswith(_nfd("يَقُولُ"))


def _assert_round3_guards(bq, text: str) -> None:
    assert parse_yes_no(text, "ar") is None                      # not a bare verdict itself
    assert not bq._DIVINE_SPEECH.search(text)                    # no God's speech (hadith qudsi out)
    assert not bq._SALAWAT.search(text)                          # no salawat: the Qur'an never has one


def test_hadith_pool_is_matn_only(bq):
    pool = bq._hadith_pool()
    assert {d["work"] for d in pool} == set(_SIX_WORKS)
    for d in pool:
        text = d["expected"]["text"]
        assert d["tradition"] == "Islam" and d["version"] == "sunnah.com Arabic"
        assert bq._script(text) == "ar" and len(text.split()) >= bq.MIN_WORDS
        assert not _opens_with_isnad(text)
        assert '"' not in text and "\u200e" not in text and "\u200f" not in text and "\n" not in text
        _assert_round3_guards(bq, text)


# --- no Qur'an wording in a donor (owner-raised) ---------------------------------------------------

@pytest.mark.parametrize("text,ayah", [
    # 33:56 quoted in Imla'i spelling inside a hadith: six shared consecutive words, across orthographies
    ("إن الله وملائكته يصلون على النبي يا أيها الذين آمنوا صلوا عليه وسلموا تسليما", "33:56"),
    # a short ayah (112:1) contained whole in a longer text
    ("ثم قرأ قل هو الله أحد حتى ختمها", "112:1"),
    # a text lying inside an ayah (2:255 / 3:2 open with it)
    ("الله لا إله إلا هو الحي القيوم", None),
])
def test_quran_overlap_catches_shared_wording(bq, text, ayah):
    hit = bq.quran_overlap(text)
    assert hit is not None
    if ayah is not None:
        assert hit == ayah


def test_quran_overlap_passes_a_clean_matn(bq):
    assert bq.quran_overlap("إنما الأعمال بالنيات وإنما لكل امرئ ما نوى فمن كانت هجرته إلى دنيا يصيبها") is None


def test_committed_islam_no_rows_quote_a_clean_hadith_matn(bq):
    raw = {
        t.work: {h["idInBook"]: h.get("arabic") or "" for h in
                 json.loads((bq.RAW / "Sunni Islam" / t.payload).read_text(encoding="utf-8"))["hadiths"]}
        for t in bq.hadith_collections()
    }
    no_rows = _no_rows(_committed_islam_rows())
    assert no_rows, "expected committed Islam verify 'no' rows"
    for r in no_rows:
        exp, quoted = r["expected"], bq._quoted_passage(r["prompt"])
        work, number = exp["true_citation"].rsplit(" ", 1)
        assert exp["true_tradition"] == "Islam" and exp["true_version"] == "sunnah.com Arabic"
        assert work in _SIX_WORKS
        assert quoted == bq.hadith_matn(raw[work][int(number)])   # the matn of the cited hadith
        assert bq._script(quoted) == "ar"                            # same script as the Qur'an
        assert not _opens_with_isnad(quoted)
        _assert_round3_guards(bq, quoted)
        assert bq.quran_overlap(quoted) is None, exp["true_citation"]


def _raw_quoted_spans(raw: str) -> list[str]:
    """Every span sunnah.com puts between a pair of quotation marks, read independently of the
    generator: split at the marks, keep the inside of each pair, drop the right-to-left marks and the
    separators just inside the opening mark, collapse whitespace."""
    inside = raw.replace("\u200e", "").replace("\u200f", "").split('"')[1::2]
    return [" ".join(re.sub(r"^[\s:،,.\-–—ـ؛]+", "", span).split()) for span in inside]


def test_committed_no_donors_are_exactly_one_quoted_span(bq):
    # architect, round 3: every committed "no" donor is exactly one quoted span of its hadith — no
    # quotation mark inside it, nothing (a narrator's remark, a second chain) after its closing mark
    raw = {
        t.work: {h["idInBook"]: h.get("arabic") or "" for h in
                 json.loads((bq.RAW / "Sunni Islam" / t.payload).read_text(encoding="utf-8"))["hadiths"]}
        for t in bq.hadith_collections()
    }
    no_rows = _no_rows(_committed_islam_rows())
    assert len(no_rows) == 38
    for r in no_rows:
        quoted = bq._quoted_passage(r["prompt"])
        work, number = r["expected"]["true_citation"].rsplit(" ", 1)
        assert '"' not in quoted and "\u200f" not in quoted and "\u200e" not in quoted
        assert r["prompt"].count('"') == 2                          # the prompt quotes exactly one span
        assert quoted in _raw_quoted_spans(raw[work][int(number)]), r["expected"]["true_citation"]


# --- the gate is the script; the donor is per row --------------------------------------------------

def _verify_row(tradition, citation, passage, *, condition="ask_english", sample="population"):
    return {
        "tradition": tradition, "citation": citation, "sample": sample, "version": "v",
        "task": "verify_source", "condition": condition,
        "prompt": f'Is the following text from X? "{passage}" Answer Yes or No.',
        "expected": {"answer": "yes"},
    }


def _quote_row(tradition, citation, text):
    return {
        "tradition": tradition, "citation": citation, "sample": "population", "version": "w", "work": "W",
        "task": "retrieve_quote", "condition": "ask_english", "prompt": "", "expected": {"text": text},
    }


def test_script_gate_english_quran_edition_gets_no_hadith(bq):
    english = "In the name of God, the Lord of Mercy, the Giver of Mercy, praise belongs to God, Lord of the Worlds"
    islam = [_verify_row("Islam", "1:1", english), _verify_row("Islam", "1:2", english)]
    other = [_quote_row("Christianity", "John 3:16", "For God so loved the world that he gave his only Son")]
    bq.add_verify_negatives({"islam": islam, "christianity": other})
    flipped = _no_rows(islam)
    assert len(flipped) == 1
    assert flipped[0]["expected"]["true_tradition"] == "Christianity"   # same script, not a hadith


def test_empty_same_tradition_only_pool_fails_fast(bq):
    rows = [_verify_row("Sikhism", "Ang 1:1", "ਸਤਿ ਨਾਮੁ"), _verify_row("Sikhism", "Ang 1:2", "ਸਤਿ ਨਾਮੁ")]
    with pytest.raises(SystemExit, match="no verify_source donor"):
        bq.add_verify_negatives({"sikhism": rows})


def test_hadith_donor_depends_only_on_the_row(bq):
    row = _no_rows(_islam_built(bq))[0]
    same = dict(row, prompt="anything else", expected={"answer": "yes"})
    assert bq._hadith_donor(same)["citation"] == row["expected"]["true_citation"]


def test_other_traditions_cannot_move_islam_donors(bq):
    alone = [(r["condition"], r["sample"], r["citation"], r["expected"]["true_citation"]) for r in _no_rows(_islam_built(bq))]
    islam = bq.islam()
    bq.add_verify_negatives({"judaism": bq.judaism(), "islam": islam, "sikhism": bq.sikhism()})
    together = [(r["condition"], r["sample"], r["citation"], r["expected"]["true_citation"]) for r in _no_rows(islam)]
    assert together == alone


# --- the committed files are what the generator builds ---------------------------------------------

def test_islam_build_reproduces_committed_question_files(bq):
    by_path: dict[Path, list[dict]] = {}
    for row in (bq._collect_row(r) for r in _islam_built(bq)):
        by_path.setdefault(bq._language_dir(row) / "questions.jsonl", []).append(row)
    assert len(by_path) == 4
    for path, group in by_path.items():
        built = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in group)
        assert path.read_text(encoding="utf-8") == built, path


def test_yes_rows_stay_quran_and_no_rows_are_half(bq):
    rows = _islam_built(bq)
    verify = [r for r in rows if r["task"] == "verify_source"]
    no_rows = _no_rows(rows)
    assert 0 < len(no_rows) < len(verify)
    for r in verify:
        if r["expected"]["answer"] == "yes":
            assert r["expected"]["true_tradition"] == "Islam"
            assert r["expected"]["true_version"] == "Uthmani (QUL)"


def test_prompts_drop_qul_but_metadata_keeps_version():
    for c in _committed_islam_rows():
        assert "QUL" not in c["prompt"]
        assert c["source"]["version"] == "Uthmani (QUL)"
        if c["source"]["condition"] == "ask_english":
            assert "the Uthmani Qur'an" in c["prompt"]


def test_samples_match_the_pr_claims(bq):
    rows = _committed_islam_rows()
    quotes = [r for r in rows if r["task"] == "retrieve_quote" and r["source"]["condition"] == "ask_native"]
    population = {r["source"]["citation"]: r["expected"]["text"] for r in quotes if r["source"]["sample"] == "population"}
    familiarity = {r["source"]["citation"] for r in quotes if r["source"]["sample"] == "familiarity"}
    famous = {p.citation for p in bq.famous_passages("The Qur'an", bq.QURAN_VERSION)}
    assert len(population) == 30
    assert familiarity == famous and len(famous) == 8
    assert not set(population) & familiarity
    assert all(len(text.split()) >= bq.MIN_WORDS for text in population.values())


# --- the review page prints the live prompt wording ------------------------------------------------

def _page_templates(page: str) -> tuple[dict[str, str], dict[str, str], str]:
    english, native, section = {}, {}, None
    suffix = re.search(r"^Each English prompt has a second line: `(.+)`$", page, re.M).group(1)
    for line in page.splitlines():
        if line.startswith("## Prompts in English"):
            section = english
        elif line.startswith("## Prompts in the text's language"):
            section = native
        elif line.startswith("## "):
            section = None
        m = re.match(r"- `(\w+)`: (.+)$", line)
        if m and section is not None:
            section[m.group(1)] = m.group(2)
    return english, native, suffix


def _as_pattern(template: str) -> re.Pattern[str]:
    rx = re.escape(template)
    for field in ("citation", "head", "text", "example"):
        rx = rx.replace(re.escape("{" + field + "}"), "(.+?)")
    return re.compile(rx, re.S)


def test_islam_review_page_is_current_and_matches_the_prompts(br):
    folder, body = br.islam()
    committed = (_REVIEW / folder / "README.md").read_text(encoding="utf-8")
    assert committed == body                                    # the committed page is the current build
    english, native, suffix = _page_templates(body)
    assert set(english) == set(native) == {"retrieve_quote", "complete_unit", "cite_passage", "verify_source"}
    for row in _committed_islam_rows():
        task, condition = row["task"], row["source"]["condition"]
        if condition == "ask_english":
            pattern = _as_pattern(f"{english[task]}\n{suffix}")
        else:
            pattern = _as_pattern(native[task])
        assert pattern.fullmatch(row["prompt"]), (task, condition, row["prompt"][:80])
