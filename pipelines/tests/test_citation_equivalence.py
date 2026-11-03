"""Issue #112: a cite_passage answer in the text's own notation is the same citation.

The native-text prompts ask the model to "answer in the language of" the edition, so a model rightly
writes ``Πράξεις 24:1`` for Acts 24:1, ``שמות כח:מג`` for Exodus 28:43, ``עירובין צ״א א׳:א׳`` for
Eruvin 91a:1. ``citations.py`` rewrites the answer into the expected's notation (labels from
``citation_aliases.yaml``) before the existing matcher compares it. Owner decision: Talmud is scored
at tractate + daf + amud and the Guru Granth Sahib at the Ang, with ``segment_match`` beside it.

The oracle at the bottom re-scores the committed 2026-11-02 cite_passage answers: the only cells the
layer moves past the #111 matcher are those registered by identity in
``testdata/citation_equivalence_movers.tsv``, and each goes incorrect -> correct. Read-only; the
committed ``scores.jsonl`` are not rewritten.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pytest
import yaml

from sacredbench import citations
from sacredbench.score import _single_citation_correct, normalize, score_answer, score_file

REPO = Path(__file__).resolve().parents[2]
RUNS = REPO / "runs"
MOVERS = Path(__file__).parent / "testdata" / "citation_equivalence_movers.tsv"


def _cite(answer: str, citation: str) -> dict:
    return score_answer("cite_passage", answer, {"citation": citation})


@pytest.mark.parametrize(
    ("answer", "citation"),
    [
        ("Πράξεις 24:1", "Acts 24:1"),
        ("Πρὸς Ἑβραίους 1:2.", "Hebrews 1:2"),
        ("Κατὰ Λουκᾶν 12:41", "Luke 12:41"),
        ("ΚΑΤΑ ΛΟΥΚΑΝ 12:41", "Luke 12:41"),
        ("Ιωάννης 12:13", "John 12:13"),  # no breathing mark
        ("Πρὸς Θεσσαλονικεῖς Βʹ 2:16.", "2 Thessalonians 2:16"),
        ("Β΄ Θεσσαλονικεῖς 2:16", "2 Thessalonians 2:16"),
        ("שמות 28:43", "Exodus 28:43"),
        ("שמות כח:מג", "Exodus 28:43"),
        ("שְׁמוֹת כ״ח:מ״ג", "Exodus 28:43"),
        ('שמות כ"ח:מ"ג', "Exodus 28:43"),
        ("שמות כח,מג", "Exodus 28:43"),
        ("Exodus כח:מג", "Exodus 28:43"),
        ("דברי הימים א ט:כב", "1 Chronicles 9:22"),
        ("מלכים א א׳:כ״ג", "1 Kings 1:23"),
        ("שמואל ב׳ י״ח:ה", "2 Samuel 18:5"),
        ("ישעיהו מט:טו", "Isaiah 49:15"),
        ("תהלים קיט:קעו", "Psalms 119:176"),
        ("עירובין 91a:1", "Eruvin 91a:1"),
        ("עירובין צ״א א׳:א׳.", "Eruvin 91a:1"),
        ("יומא ע״ח ב:א", "Yoma 78b:1"),
        ('שבת צו ע"א:א', "Shabbat 96a:1"),
        ("آل عمران: ١٤٠", "3:140"),  # was a #111 negative: the surah is named, not numbered
        ("آل عمران:174", "3:174"),
        ("هذه الآية في سورة لقمان، الآية 12", "31:12"),
        ("धम्मपद १०६", "Dhammapada 106"),
        ("Dhammapadaṃ 359", "Dhammapada 359"),
        ("This is John 8:41. In Greek: Ἰωάννης 8:41", "John 8:41"),  # one citation, two notations
    ],
)
def test_native_notation_is_the_same_citation(answer, citation):
    scored = _cite(answer, citation)
    assert (scored["outcome"], scored["n_candidates"]) == ("correct", 1)
    assert scored.get("segment_match", 1) == 1


def test_gurmukhi_label_is_ang():
    # The #111 numerals-only negative: the whole citation, label included, in Gurmukhi.
    assert _cite("ਅੰਗ ੭੩੪:੮", "Ang 734:8") == {"correct": 1, "n_candidates": 1, "segment_match": 1, "outcome": "correct"}


@pytest.mark.parametrize(
    ("answer", "citation"),
    [
        ("Rosh Hashanah 21a:5", "Rosh Hashanah 21a:2"),
        ("Rosh Hashanah 21a", "Rosh Hashanah 21a:2"),  # the conventional citation
        ("ראש השנה כ״א א:ו", "Rosh Hashanah 21a:2"),
        ("Ang 1297:15", "Ang 1297:28"),
        ("ਅੰਗ ੧੨੯੭:੧੫", "Ang 1297:28"),
    ],
)
def test_talmud_and_ggs_score_at_the_conventional_unit(answer, citation):
    assert _cite(answer, citation) == {"correct": 1, "n_candidates": 1, "segment_match": 0, "outcome": "correct"}


def test_segment_match_is_the_full_granularity_verdict():
    assert _cite("Rosh Hashanah 21a:2", "Rosh Hashanah 21a:2")["segment_match"] == 1
    assert _cite("Rosh Hashanah 21b:2", "Rosh Hashanah 21a:2")["segment_match"] == 0
    assert "segment_match" not in _cite("Exodus 28:43", "Exodus 28:43")  # not a segment-indexed edition


def test_granularity_switch(monkeypatch):
    monkeypatch.setattr(citations, "HEADLINE_DROPS_SEGMENT", False)
    assert _cite("Rosh Hashanah 21a:5", "Rosh Hashanah 21a:2")["outcome"] == "incorrect"
    assert _cite("Ang 1297:15", "Ang 1297:28")["outcome"] == "incorrect"
    assert _cite("עירובין צ״א א׳:א׳", "Eruvin 91a:1")["outcome"] == "correct"  # notation still counts


@pytest.mark.parametrize(
    ("answer", "citation"),
    [
        ("ויקרא ה׳:י״ט", "Leviticus 14:19"),  # wrong chapter (committed)
        ("מלכים א' כא:יח", "1 Kings 22:39"),  # wrong locus (committed)
        ("שמות כח:מד", "Exodus 28:43"),
        ("נדרים נ״ב א", "Nedarim 52b:2"),  # amud a, not b
        ("Rosh Hashanah 21b:2", "Rosh Hashanah 21a:2"),
        ("Rosh Hashanah 22a:2", "Rosh Hashanah 21a:2"),
        ("Bekhorot 1:1", "Bekhorot 1a:1"),  # a Mishnah citation is not daf 1
        ("Ang 1296:23", "Ang 1297:23"),
        ("Λουκᾶς 12:42", "Luke 12:41"),
        ("التوبة:25", "9:24"),
    ],
)
def test_wrong_loci_stay_incorrect(answer, citation):
    assert _cite(answer, citation)["outcome"] == "incorrect"


@pytest.mark.parametrize(
    ("answer", "citation"),
    [
        ("שמות כח:מג או ויקרא ה:יט", "Exodus 28:43"),
        ("Πράξεις 24:1 ἢ Πράξεις 24:2", "Acts 24:1"),
        ("Rosh Hashanah 21a:2 or 22b:1", "Rosh Hashanah 21a:2"),
    ],
)
def test_two_different_citations_are_still_a_hedge(answer, citation):
    assert _cite(answer, citation)["outcome"] == "incorrect"
    # the rewritten answer holds two distinct citations (n_candidates is only replaced on credit)
    assert _single_citation_correct(citations.canonical_citation_text(answer, citation), citation) == (0, 2)


def test_summary_records_the_switch_and_aggregates_segment_match(tmp_path, monkeypatch):
    talmud = {"work": "Babylonian Talmud", "version": "William Davidson", "language": "arc"}
    exodus = {"work": "Tanakh", "version": "Masoretic Text", "language": "he"}
    cells = [
        ("Eruvin 18a", "Eruvin 18a:15", talmud),  # correct at the daf, segment_match 0
        ("Eruvin 18a:15", "Eruvin 18a:15", talmud),  # correct, segment_match 1
        ("Eruvin 18b", "Eruvin 18a:15", talmud),  # incorrect: not counted
        ("Exodus 28:43", "Exodus 28:43", exodus),  # not segment-indexed: not counted
    ]
    answers = tmp_path / "answers.jsonl"
    answers.write_text("".join(
        json.dumps({
            "question_id": f"q{i}", "model_id": "m1", "task": "cite_passage", "question_set_digest": "d",
            "answer": answer, "question": {"expected": {"citation": citation}, "source": source},
        }) + "\n"
        for i, (answer, citation, source) in enumerate(cells)
    ), encoding="utf-8")
    summary = score_file(answers, tmp_path / "scores.jsonl")
    assert summary["headline_drops_segment"] is True
    assert summary["segment_match"] == {
        "m1": {"\u0000".join(talmud.values()): {"correct": 2, "segment_match": 1}},
    }
    assert summary["models"]["m1"]["cite_passage"]["correct"] == 3
    monkeypatch.setattr(citations, "HEADLINE_DROPS_SEGMENT", False)
    strict = score_file(answers, tmp_path / "scores.jsonl")
    assert strict["headline_drops_segment"] is False
    assert strict["segment_match"]["m1"]["\u0000".join(talmud.values())] == {"correct": 1, "segment_match": 1}


@pytest.mark.parametrize("answer", ["Ang 1297:15 or John 1:1", "ਅੰਗ ੧੨੯੭:੧੫ ਜਾਂ John 1:1", "John 1:1 / Ang 1297"])
def test_a_colon_rival_beside_an_ang_is_still_a_hedge(answer):
    # "Ang 1297:28" scored at the Ang loses its colon; the full citation's colon rivals still count
    assert _cite(answer, "Ang 1297:28")["outcome"] == "incorrect"
    assert _cite(answer.replace("John 1:1", "").strip(" /ਜਾਂor"), "Ang 1297:28")["outcome"] == "correct"


@pytest.mark.parametrize(
    ("token", "value"),
    [("א", 1), ("כח", 28), ("כ״ח", 28), ('כ"ח', 28), ("טו", 15), ("טז", 16), ("קעו", 176), ("שמות", None)],
)
def test_hebrew_numeral(token, value):
    assert citations.hebrew_numeral(token) == value


def test_shared_normalize_and_other_tasks_untouched():
    assert normalize("Πράξεις 24:1") == "πραξεισ 24 1"
    assert score_answer("retrieve_quote", "שמות", {"text": "Exodus"})["correct"] == 0


# --- the alias data -----------------------------------------------------------------------------


def _editions() -> dict[str, dict]:
    data = yaml.safe_load(citations.ALIASES_PATH.read_text(encoding="utf-8"))
    return {e["edition"]: e for e in data["editions"]}


def test_alias_tables_are_complete():
    editions = _editions()
    sizes = {name: len(e.get("labels") or e.get("chapter_names")) for name, e in editions.items()}
    assert sizes == {
        "Greek New Testament (Scrivener 1894)": 27,
        "Masoretic Text (Westminster Leningrad Codex)": 39,
        "Babylonian Talmud (William Davidson)": 37,
        "Sri Guru Granth Sahib (Shabad OS)": 1,
        "Dhammapada (Chaṭṭha Saṅgāyana)": 1,
        "Uthmani Qur'an": 114,
    }
    assert sorted(editions["Uthmani Qur'an"]["chapter_names"]) == list(range(1, 115))
    citations._tables()  # builds, and fails on an alias that maps to two labels


def test_talmud_names_are_the_sefaria_hebrew_titles():
    tractates = _editions()["Babylonian Talmud (William Davidson)"]["labels"]
    sources = sorted((REPO / "texts/raw/Judaism/Talmud Bavli").glob("* - he - *.json"))
    assert sources
    for path in sources:
        meta = json.loads(path.read_text(encoding="utf-8"))
        assert meta["heTitle"] in tractates[meta["title"]], path.name


def test_every_expected_label_in_the_native_sets_has_an_alias():
    t = citations._tables()
    labels = set(t.native.values())
    for folder in ("christianity/native", "judaism/native", "sikhism/native", "buddhism/native"):
        for path in (REPO / "items/for-test" / folder).rglob("questions.jsonl"):
            for line in path.read_text(encoding="utf-8").splitlines():
                q = json.loads(line)
                if q["task"] == "cite_passage":
                    label = q["expected"]["citation"].rsplit(" ", 1)[0].casefold()
                    assert label in labels, (path, q["expected"]["citation"])


# --- oracle over the committed 2026-11-02 run ----------------------------------------------------


def _registered() -> dict[tuple[str, int, str], tuple[str, int]]:
    rows = [l.split("\t") for l in MOVERS.read_text(encoding="utf-8").splitlines() if l and not l.startswith("#")]
    registered = {(folder, int(row), qid): (kind, int(n)) for folder, row, qid, kind, n in rows}
    assert len(registered) == len(rows)
    return registered


def test_registered_mover_counts():
    by_kind = Counter((folder.split("/", 2)[2], kind) for (folder, _, _), (kind, _) in _registered().items())
    assert by_kind == {
        ("christianity/native/greek/population/prompt-english", "notation"): 89,
        ("christianity/native/greek/population/prompt-native", "notation"): 2,
        ("christianity/native/masoretic/population/prompt-english", "notation"): 180,
        ("christianity/native/masoretic/population/prompt-native", "notation"): 1,
        ("islam/native/population/prompt-english", "notation"): 8,
        ("islam/native/population/prompt-native", "notation"): 1,
        ("judaism/native/population/prompt-english", "notation"): 16,
        ("sikhism/native/population/prompt-english", "notation"): 1,
        ("judaism/english/population", "granularity"): 115,
        ("judaism/native/population/prompt-english", "granularity"): 89,
        ("judaism/native/population/prompt-native", "granularity"): 81,
        ("sikhism/native/population/prompt-english", "granularity"): 36,
        ("sikhism/native/population/prompt-native", "granularity"): 34,
    }


def test_committed_cite_passage_cells_move_only_as_registered():
    registered = _registered()
    score_files = sorted(RUNS.glob("*/base/**/scores.jsonl"))
    if not score_files:
        pytest.skip("runs/ evidence not present")
    seen: set[tuple[str, int, str]] = set()
    for scores in score_files:
        folder = scores.parent.relative_to(RUNS).as_posix()
        answers = [json.loads(l) for l in scores.with_name("answers.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
        for i, row in enumerate(answers):
            if row["task"] != "cite_passage":
                continue
            citation = row["question"]["expected"]["citation"]
            old_correct, old_n = _single_citation_correct(row["answer"], citation)  # the #111 matcher
            new = citations.score_citation(row["answer"], citation)
            key = (folder, i, row["question_id"])
            if key not in registered:
                assert (new["correct"], new["n_candidates"]) == (old_correct, old_n), f"{key} moved but is not registered"
                continue
            seen.add(key)
            kind, n = registered[key]
            assert (old_correct, new["correct"], new["n_candidates"]) == (0, 1, n), key
            assert new.get("segment_match", 1) == (0 if kind == "granularity" else 1), key
    assert seen == set(registered), f"registered cells missing from runs/: {sorted(set(registered) - seen)[:5]}"
