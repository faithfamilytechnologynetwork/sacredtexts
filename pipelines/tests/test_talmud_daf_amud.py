"""Issue #147: the native Talmud arms name the Vilna text and ask at daf+amud.

Naming Sefaria's "William Davidson Aramaic edition" drew some 200 copyright refusals per native arm in
``runs/facct-2026-11-03`` on what is the public-domain Vilna text, so every native Talmud prompt names
"the Talmud Bavli (Vilna text)" / "התלמוד הבבלי (נוסח וילנא)". The ``:3`` of ``Megillah 23b:3`` is
Sefaria's own paragraph split, which no model can know, so retrieve_quote asks for the text at the
beginning of the amud (expecting its first segment, ``Megillah 23b:1``, which is the row's source
citation) and cite_passage expects ``Megillah 23b``. The English (Davidson/Steinsaltz) arm is unchanged.

Scoring a bare daf+amud (``citations._score_at_daf``): Hebrew notation is rewritten and a volunteered
segment is dropped, so ``Megillah 23b:3`` and ``מגילה כ״ג ב:ג`` are Megillah 23b; the headline is that
verdict alone (no containment fallback) and ``segment_match`` is None.

The oracle at the bottom re-scores every committed native Talmud cite cell against the bare daf+amud
(its form example too): no outcome moves from the #112 daf+amud headline. Read-only.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

import pytest

from sacredbench import citations
from sacredbench.score import example_citation, score_answer, score_file

REPO = Path(__file__).resolve().parents[2]
RUN = REPO / "runs" / "facct-2026-11-03"
JUDAISM = REPO / "items" / "for-test" / "judaism"
TALMUD_RAW = REPO / "texts" / "raw" / "Judaism" / "Talmud Bavli"
PROMPT = (
    'Where in the Talmud Bavli (Vilna text) can I find this quote? "…" '
    "Answer with the citation only, in the same form as: Gittin 40a.\n"
    "Answer in the language of the Talmud Bavli (Vilna text)."
)
AT_DAF = {"correct": 1, "n_candidates": 1, "segment_match": None, "outcome": "correct"}


def _cite(answer: str, citation: str = "Megillah 23b", prompt: str | None = PROMPT) -> dict:
    return score_answer("cite_passage", answer, {"citation": citation}, prompt=prompt)


@pytest.mark.parametrize(
    "answer",
    [
        "Megillah 23b", "Megillah 23b.", "Megillah 23b:3", "Megillah 23b:1, Megillah 23b:4",
        "This passage is in Megillah 23b.", "Megillah 23b: the Mishnah on reading the Torah",
        "מגילה כ״ג ב", "מגילה כג ע״ב", "מגילה כ״ג ב:ג", 'מגילה כ"ג ע"ב:ג׳', "Megillah 23b (not Gittin 40a)",
    ],
)
def test_the_daf_and_amud_is_the_citation(answer):
    assert _cite(answer) == AT_DAF


@pytest.mark.parametrize("answer", ["Megillah 23a", "Megillah 24b", "מגילה כג א", "Gittin 23b", "Megillah 23", "Gittin 40a"])
def test_another_daf_amud_or_tractate_is_wrong(answer):
    assert _cite(answer)["outcome"] == "incorrect"


@pytest.mark.parametrize("answer", ["Megillah 23b or Megillah 24a", "Megillah 23b:3 or Megillah 23a:3", "מגילה כ״ג ב או מגילה כ״ד א"])
def test_a_second_daf_is_a_hedge(answer):
    assert _cite(answer) == {"correct": 0, "n_candidates": 2, "segment_match": None, "outcome": "incorrect"}


def test_the_granularity_switch_does_not_apply_to_a_bare_daf(monkeypatch):
    monkeypatch.setattr(citations, "HEADLINE_DROPS_SEGMENT", False)
    assert _cite("Megillah 23b:3") == AT_DAF  # no segment in the expected to hold it to
    assert _cite("Megillah 23b:3", "Megillah 23b:1")["outcome"] == "incorrect"  # a segment expected still is


def test_a_segment_expected_is_scored_as_before():
    """The English Talmud arm keeps its segment expecteds and the #112 path."""
    assert _cite("Megillah 23b:3", "Megillah 23b:1") == {"correct": 1, "n_candidates": 1, "segment_match": 0, "outcome": "correct"}


def test_summary_leaves_a_bare_daf_out_of_segment_match(tmp_path):
    source = {"work": "Talmud Bavli", "version": "William Davidson Edition - Aramaic", "language": "he"}
    cells = [("מגילה כ״ג ב:ג", "Megillah 23b"), ("Gittin 40a:3", "Gittin 40a:1")]
    answers = tmp_path / "answers.jsonl"
    answers.write_text("".join(
        json.dumps({
            "question_id": f"q{i}", "model_id": "m1", "task": "cite_passage", "question_set_digest": "d",
            "answer": answer, "question": {"expected": {"citation": citation}, "source": source, "prompt": PROMPT},
        }) + "\n"
        for i, (answer, citation) in enumerate(cells)
    ), encoding="utf-8")
    summary = score_file(answers, tmp_path / "scores.jsonl")
    assert summary["models"]["m1"]["cite_passage"]["correct"] == 2
    assert summary["segment_match"] == {"m1": {"\u0000".join(source.values()): {"correct": 1, "segment_match": 0}}}


# --- the committed Judaism question files -------------------------------------------------------


def _rows(kind: str) -> dict[Path, list[dict]]:
    paths = sorted((JUDAISM / kind).rglob("questions.jsonl"))
    return {p: [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines()] for p in paths}


def _first_segments() -> dict[str, str]:
    """Each amud's first segment, read straight from the Sefaria payload (Aramaic)."""
    tag = re.compile(r"<[^>]+>")
    out = {}
    for path in TALMUD_RAW.glob("* - he - William Davidson Edition - Aramaic.json"):
        tract = path.name.split(" - he - ")[0]
        for i, section in enumerate(json.loads(path.read_text(encoding="utf-8"))["text"]):
            if section and isinstance(section[0], str):
                out[f"{tract} {i // 2 + 1}{'ab'[i % 2]}"] = re.sub(r"\s+", " ", html.unescape(tag.sub("", section[0]))).strip()
    return out


def test_no_native_talmud_prompt_names_the_davidson_edition():
    native = _rows("native")
    assert len(native) == 4
    for path, rows in native.items():
        for q in rows:
            assert "Davidson" not in q["prompt"] and "דייווידסון" not in q["prompt"], (path, q["id"])
            assert "the Talmud Bavli (Vilna text)" in q["prompt"] or "התלמוד הבבלי (נוסח וילנא)" in q["prompt"] \
                or "בתלמוד הבבלי (נוסח וילנא)" in q["prompt"], (path, q["id"])
            assert q["source"]["version"] == "William Davidson Edition - Aramaic"  # provenance keeps the edition


AMUD = re.compile(r"(?:the text at the beginning of (.+? \d+[ab]) in )|(?:מהו הנוסח בתחילת (.+? \d+[ab]) בתלמוד)")


def test_native_talmud_retrieve_rows_ask_for_the_beginning_of_the_amud():
    first = _first_segments()
    n = 0
    for path, rows in _rows("native").items():
        retrieve = [q for q in rows if q["task"] == "retrieve_quote"]
        amudim = []
        for q in retrieve:
            assert not re.search(r"\d+[ab]:\d+", q["prompt"]), q["id"]  # no Sefaria segment in the question
            m = AMUD.search(q["prompt"])
            assert m, q["id"]
            amud = m[1] or m[2]
            assert q["expected"] == {"text": first[amud]}, q["id"]
            assert q["source"]["citation"] == f"{amud}:1", q["id"]  # the citation names the text expected
            amudim.append(amud)
        assert len(amudim) == len(set(amudim)), path  # one retrieve row per amud
        cited = {q["expected"]["citation"] for q in rows if q["task"] == "cite_passage"}
        assert set(amudim) == cited, path  # each asks about the amud of a passage a cite row quotes
        n += len(retrieve)
    assert n == 62  # 30 population + 1 familiarity passage, two prompt arms


def test_native_talmud_cite_rows_expect_the_daf_and_amud():
    n = 0
    for path, rows in _rows("native").items():
        for q in [q for q in rows if q["task"] == "cite_passage"]:
            expected = q["expected"]["citation"]
            assert re.fullmatch(r".+? \d+[ab]", expected), q["id"]
            assert q["source"]["citation"].rpartition(":")[0] == expected, q["id"]  # the passage keeps its segment
            example = example_citation(q["prompt"])
            assert re.fullmatch(r".+? \d+[ab]", example) and example != expected, q["id"]
            n += 1
    assert n == 62


def test_the_english_talmud_arm_keeps_its_segments():
    for path, rows in _rows("english").items():
        for q in rows:
            assert "the William Davidson English edition of the Babylonian Talmud" in q["prompt"], (path, q["id"])
            if q["task"] == "cite_passage":
                assert re.fullmatch(r".+? \d+[ab]:\d+", q["expected"]["citation"]), q["id"]


# --- oracle over the committed facct-2026-11-03 run ---------------------------------------------

# Cells whose outcome holds at the bare daf+amud but whose n_candidates differs: the #112 headline took
# n from the raw matcher, which reads "Megillah 23b:3" as "megillah 23" and never reads Hebrew notation.
# failure_kind reads n_candidates (hedge / wrong_locus / no_citation), so a change here must show up.
AT_DAF_N_ONLY = 106


def _at_daf(citation: str) -> str:
    return re.sub(r"( \d+[ab]):\d+$", r"\1", citation)


def test_no_committed_native_talmud_cite_cell_moves_at_the_daf():
    """Every committed native Talmud cite cell, rescored against its bare daf+amud with the form example
    at the daf too, keeps its committed #112 outcome. Once the run is re-collected with bare expecteds,
    ``test_sggs_ang_only.test_no_committed_cite_cell_moves``'s identity check is the whole check."""
    score_files = sorted(RUN.glob("*/base/judaism/native/**/scores.jsonl"))
    if not score_files:
        pytest.skip("runs/ evidence not present")
    n = {"segment": 0, "daf": 0}
    moved, n_only = {}, 0
    for scores in score_files:
        answers = [json.loads(l) for l in scores.with_name("answers.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
        committed = [json.loads(l) for l in scores.read_text(encoding="utf-8").splitlines() if l.strip()]
        for row, score in zip(answers, committed, strict=True):
            assert row["question_id"] == score["question_id"], scores
            if row["task"] != "cite_passage":
                continue
            question, key = row["question"], (scores.relative_to(RUN).as_posix(), row["question_id"])
            expected = question["expected"]["citation"]
            if expected == _at_daf(expected):
                n["daf"] += 1  # already a bare daf+amud expected: identity is checked by test_sggs_ang_only
                continue
            n["segment"] += 1
            head, sep, tail = question["prompt"].rpartition('"')
            example = example_citation(question["prompt"])
            prompt = head + sep + tail.replace(f": {example}", f": {_at_daf(example)}", 1)
            at_daf = score_answer("cite_passage", row["answer"], {"citation": _at_daf(expected)}, prompt=prompt)
            assert at_daf["segment_match"] is None, key
            if at_daf["outcome"] != score["metrics"]["outcome"]:
                moved[key] = (score["metrics"]["outcome"], at_daf["outcome"])
            elif at_daf["n_candidates"] != score["metrics"]["n_candidates"]:
                n_only += 1
    assert n["segment"] + n["daf"] == 960, n
    assert n["segment"] in (0, 960), n
    if n["segment"]:
        assert moved == {}
        assert n_only == AT_DAF_N_ONLY
