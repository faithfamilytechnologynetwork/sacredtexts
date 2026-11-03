"""Issues #90, #91, #113 and #116: every prompt names its work, and one command rebuilds every question set.

``items/for-test/review/build_questions.py``'s ``main`` builds every set's rows, draws every verify
"no" row from one pool by METHODOLOGY.md's donor table, and writes each set. The test runs that
build offline: the three fetched texts (NRSV from oremus, the Masoretic text and the Greek New
Testament at pinned commits) are replaced by the wording committed beside the questions.

What is pinned:
- the build reproduces every committed questions.jsonl byte for byte, and the passages.json it writes;
- each English prompt names the work, not a bare catalogue version ("from 2013 edition?", #90), and the
  Sanskrit prompts name it in their own language instead of splicing in the English name;
- the Pali Dhammapada is asked with the English prompt only: there is no romanized-Pali prompt arm (#113);
- every committed "no" row quotes the donor METHODOLOGY.md's table names for that edition (this is what
  retarget_verify.py used to apply after the build), and each set flips half its verify rows;
- no file repeats a prompt, and no set quotes one "no" donor twice (#116);
- every prompt that quotes a passage quotes exactly one, and a verify prompt's passage is the one its
  expected answer names: its own for "yes", the donor for "no" (PR #98: a splice between the first two
  quotation marks left five encyclical "no" rows with a donor glued onto the encyclical's tail).
"""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
_ITEMS = _REPO / "items" / "for-test"
_REVIEW = _ITEMS / "review"
_NT = {
    "Matthew", "Mark", "Luke", "John", "Acts", "Romans", "1 Corinthians", "2 Corinthians",
    "Galatians", "Ephesians", "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians",
    "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews", "James", "1 Peter", "2 Peter",
    "1 John", "2 John", "3 John", "Jude", "Revelation",
}
_MASORETIC = "the Masoretic Text (Westminster Leningrad Codex)"
_GREEK = "the Greek New Testament (Scrivener 1894)"
# catalogue version -> the work an English prompt must name (#90); an encyclical names its own work
_WORK = {
    "2013 edition": "Book of Mormon",
    "William Davidson Edition - Aramaic": "Babylonian Talmud",
    "William Davidson Edition - English": "Babylonian Talmud",
    "Shabad OS (SGPC Shabadaarth)": "Sri Guru Granth Sahib",
    "Stotra Samhita (Gita Press text)": "Bhagavad Gita",
    "Annie Besant (1922)": "Bhagavad Gita",
    "Chaṭṭha Saṅgāyana (VRI)": "Dhammapada",
    "Uthmani (QUL)": "Qur'an",
    "NRSV": "New Revised Standard Version",
    _MASORETIC: "Masoretic Text",
    _GREEK: "Greek New Testament",
}
_NATIVE_EDITIONS = {
    "William Davidson Edition - Aramaic", "Uthmani (QUL)", "Shabad OS (SGPC Shabadaarth)",
    "Stotra Samhita (Gita Press text)", "Chaṭṭha Saṅgāyana (VRI)", _MASORETIC, _GREEK,
}


def _rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _committed() -> dict[Path, list[dict]]:
    paths = sorted(p for p in _ITEMS.rglob("questions.jsonl") if "review" not in p.parts)
    assert len(paths) == 36
    return {p: _rows(p) for p in paths}


def _outside_quote(prompt: str) -> str:
    a, b = prompt.find('"'), prompt.rfind('"')
    return prompt if a == -1 else prompt[:a] + prompt[b + 1:]


def _passages(*parts: str) -> dict[str, str]:
    out = {}
    for sample in ("population", "familiarity"):
        payload = json.loads((_ITEMS.joinpath(*parts, sample, "passages.json")).read_text(encoding="utf-8"))
        out.update({p["citation"]: next(iter(p["text"].values())) for p in payload["passages"]})
    return out


@pytest.fixture(scope="module")
def builders():
    sys.path.insert(0, str(_REVIEW))
    try:
        yield importlib.import_module("build_questions"), importlib.import_module("build_christian_original")
    finally:
        sys.path.remove(str(_REVIEW))


@pytest.fixture(scope="module")
def rebuilt(builders) -> dict[Path, str]:
    bq, bco = builders
    nrsv = _passages("christianity", "english")
    masoretic = _passages("christianity", "native", "masoretic")
    greek = _passages("christianity", "native", "greek")

    def wlc_books(citations):
        keyed = {}
        for citation, text in masoretic.items():
            book, chapter, verse = bco.split_cite(citation)
            keyed[f"{bco.OSIS[book]}.{chapter}.{verse}"] = text
        return keyed

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(bq, "fetch_nrsv", nrsv.__getitem__)
        mp.setattr(bco, "wlc_books", wlc_books)
        mp.setattr(bco, "greek_index", lambda: {bco.split_cite(c): t for c, t in greek.items()})
        return bq.output_files(bq.build_all())


# --- #91: one command rebuilds every set ------------------------------------------------------------

def test_the_build_writes_exactly_the_committed_question_files(rebuilt):
    assert {p for p in rebuilt if p.name == "questions.jsonl"} == set(_committed())


def test_every_committed_file_is_what_the_build_writes(rebuilt):
    for path, text in rebuilt.items():
        assert path.read_text(encoding="utf-8") == text, path.relative_to(_ITEMS)


def test_fetched_texts_record_a_pinned_source(rebuilt):
    for path, text in rebuilt.items():
        if path.name == "passages.json" and "christianity" in path.parts:
            provenance = json.loads(text)["provenance"]
            assert provenance.startswith("https://"), path
            if "github" in provenance:
                assert "/master/" not in provenance and "/main/" not in provenance, path


# --- #90: every prompt names the work ---------------------------------------------------------------

def test_edition_name_names_the_work(builders):
    bq, _ = builders
    for version, work in _WORK.items():
        if version in bq._EDITION_DISPLAY:
            assert work in bq.edition_name(version), version
    encyclical = bq.edition_name("Vatican English text (Benedict XVI, 2005-12-25)", "Deus caritas est")
    assert "Deus caritas est" in encyclical and "2005-12-25" in encyclical


def test_an_edition_without_a_display_name_fails_fast(builders):
    bq, _ = builders
    with pytest.raises(SystemExit, match="no prompt name for edition"):
        bq.edition_name("Some Other Edition (2020)")


def test_every_english_prompt_names_its_work():
    for path, rows in _committed().items():
        for row in rows:
            source = row["source"]
            if source["condition"] == "ask_native" or source["version"] == "Saheeh International (QUL)":
                continue  # native prompts are checked below; Saheeh is owner-signed as is (#75)
            work = source["work"] if source["version"].startswith("Vatican English text") else _WORK[source["version"]]
            words = _outside_quote(row["prompt"])
            assert work in words, (path.relative_to(_ITEMS), words[:120])
            assert "from 2013 edition" not in words and "in 2013 edition" not in words


def test_sanskrit_prompts_name_the_work_in_their_own_language():
    paths = list((_ITEMS / "hinduism" / "native").rglob("prompt-native/questions.jsonl"))
    assert paths
    for path in paths:
        for row in _rows(path):
            words = _outside_quote(row["prompt"])
            assert "श्रीमद्भगवद्गीता" in words and "edition" not in words, (path.relative_to(_ITEMS), words[:120])


# --- #113: the Pali Dhammapada has no Pali-language prompt arm ---------------------------------------

def test_buddhism_is_asked_with_the_english_prompt_only(rebuilt):
    """Romanized Pali has no native speakers, so its native prompt is not comparable to the others (#113)."""
    buddhism = _ITEMS / "buddhism" / "native"
    for files in (set(rebuilt), set(_committed())):
        ours = {p.relative_to(buddhism).as_posix() for p in files if buddhism in p.parents and p.name == "questions.jsonl"}
        assert ours == {"population/prompt-english/questions.jsonl", "familiarity/prompt-english/questions.jsonl"}
    assert not list(buddhism.rglob("prompt-native"))
    for sample in ("population", "familiarity"):
        rows = _rows(buddhism / sample / "prompt-english" / "questions.jsonl")
        assert {r["source"]["condition"] for r in rows} == {"ask_english"}
        cited = {r["source"]["citation"] for r in rows if r["task"] == "retrieve_quote"}
        passages = json.loads((buddhism / sample / "passages.json").read_text(encoding="utf-8"))["passages"]
        assert cited == {p["citation"] for p in passages}


# --- the donor table (METHODOLOGY.md), which retarget_verify.py used to apply after the build -------

def _script(text: str) -> str:
    for ch in text:
        for name, lo, hi in (("he", 0x0590, 0x05FF), ("ar", 0x0600, 0x06FF), ("sa", 0x0900, 0x097F),
                             ("pa", 0x0A00, 0x0A7F), ("grc", 0x0370, 0x03FF)):
            if lo <= ord(ch) <= hi:
                return name
    return "lat"


def _donor_follows_the_table(row: dict) -> bool:
    source, expected = row["source"], row["expected"]
    tradition, version, english = source["tradition"][0], source["version"], source["condition"] == "en_ask_en_answer"
    donor_tradition, donor_version = expected["true_tradition"], expected["true_version"]
    if tradition == "Islam":
        return donor_tradition == "Islam" and donor_version.startswith("sunnah.com")  # a hadith (#75)
    if donor_tradition == tradition:
        return False
    if tradition == "Judaism" and not english:
        return donor_version == _MASORETIC
    if tradition == "Judaism":
        return donor_version == "NRSV" and expected["true_citation"].rsplit(" ", 1)[0] not in _NT
    if version == "NRSV":
        return donor_tradition == "Book of Mormon"
    if version == _MASORETIC:
        return donor_version == "William Davidson Edition - Aramaic"
    if tradition in ("Book of Mormon", "Encyclicals"):
        return {tradition, donor_tradition} == {"Book of Mormon", "Encyclicals"}
    if english:
        return donor_version not in _NATIVE_EDITIONS
    # Greek NT, Guru Granth Sahib, Sanskrit Gita, Pali Dhammapada: another tradition's native passage, other script
    own = _script(next(r["expected"]["text"] for r in _ROWS_BY_CITATION[(tradition, version, source["sample"])]))
    return donor_version in _NATIVE_EDITIONS and _script(_quoted(row["prompt"])) != own


def _quoted(prompt: str) -> str:
    a = prompt.find('"')
    return prompt[a + 1:prompt.find('"', a + 1)]


_ROWS_BY_CITATION: dict[tuple[str, str, str], list[dict]] = {}


def test_every_no_row_quotes_the_donor_the_table_names():
    committed = _committed()
    for rows in committed.values():
        for row in rows:
            if row["task"] == "retrieve_quote":
                s = row["source"]
                _ROWS_BY_CITATION.setdefault((s["tradition"][0], s["version"], s["sample"]), []).append(row)
    for path, rows in committed.items():
        for row in rows:
            if row["task"] == "verify_source" and row["expected"]["answer"] == "no":
                assert _donor_follows_the_table(row), (path.relative_to(_ITEMS), row["expected"])


def test_each_set_flips_half_its_verify_rows():
    for path, rows in _committed().items():
        verify = [r for r in rows if r["task"] == "verify_source"]
        no = [r for r in verify if r["expected"]["answer"] == "no"]
        assert len(no) == len(verify) // 2, path.relative_to(_ITEMS)
        assert all(r["source"]["citation"] == "" for r in no)


def test_question_ids_are_unique():
    ids = [row["id"] for rows in _committed().values() for row in rows]
    assert len(ids) == len(set(ids))


def test_no_file_repeats_a_prompt_or_a_verify_donor():
    """#116: a donor drawn with replacement asked one "no" item up to four times in a set. An encyclical's
    prompt names its own encyclical, so a repeated donor there is a repeated quoted text, not prompt."""
    for path, rows in _committed().items():
        prompts = [row["prompt"] for row in rows]
        assert len(prompts) == len(set(prompts)), path.relative_to(_ITEMS)
        donors = [_quoted(r["prompt"]) for r in rows if r["task"] == "verify_source" and r["expected"]["answer"] == "no"]
        assert len(donors) == len(set(donors)), path.relative_to(_ITEMS)


# --- PR #98: each prompt quotes one passage, and a "no" row quotes exactly its donor -----------------

_QUOTING_TASKS = ("complete_unit", "cite_passage", "verify_source")


def _in_prompt(text: str) -> str:
    """An English passage as it is quoted inside a prompt: its own quotation marks become ' (restated)."""
    return text.replace('"', "'").replace("\u201c", "'").replace("\u201d", "'")


def test_every_quoting_prompt_quotes_exactly_one_passage():
    for path, rows in _committed().items():
        for row in rows:
            if row["task"] in _QUOTING_TASKS:
                assert row["prompt"].count('"') == 2, (path.relative_to(_ITEMS), row["id"], row["prompt"][:120])


def test_every_verify_passage_is_the_one_its_expected_answer_names(builders):
    bq, _ = builders
    committed = _committed()
    passages: dict[tuple[str, str, str], str] = {}
    for rows in committed.values():
        for row in rows:
            if row["task"] == "retrieve_quote":
                s = row["source"]
                passages[(s["tradition"][0], s["version"], s["citation"])] = row["expected"]["text"]
    for donor in (*bq._hadith_pool(), *bq._english_hadith_pool()):  # the hadith donors are not question rows
        passages[(donor["tradition"], donor["version"], donor["citation"])] = donor["expected"]["text"]
    checked = 0
    for path, rows in committed.items():
        for row in rows:
            if row["task"] != "verify_source":
                continue
            e, prompt = row["expected"], row["prompt"]
            quoted = prompt[prompt.find('"') + 1:prompt.rfind('"')]  # everything the quotation marks enclose
            text = passages[(e["true_tradition"], e["true_version"], e["true_citation"])]
            assert quoted in (text, _in_prompt(text)), (path.relative_to(_ITEMS), row["id"], e["answer"], e["true_citation"])
            checked += 1
    assert checked == sum(1 for rows in committed.values() for r in rows if r["task"] == "verify_source")


def test_a_no_row_is_its_template_rendered_around_the_donor(builders):
    bq, _ = builders
    row = bq.prompt_for(bq.EN["verify_source"], {"version": "the 2013 edition of the Book of Mormon", "text": "own"}, "\nX")
    assert row["prompt"] == 'Is the following text from the 2013 edition of the Book of Mormon? "own" Answer Yes or No.\nX'
    assert row["render"]("donor") == 'Is the following text from the 2013 edition of the Book of Mormon? "donor" Answer Yes or No.\nX'
    with pytest.raises(SystemExit, match="straight double quote"):
        row["render"]('a passage that "quotes" something')
    with pytest.raises(SystemExit, match="straight double quote"):
        bq.prompt_for(bq.EN["verify_source"], {"version": "v", "text": 'it says "this"'})
