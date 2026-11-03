"""Issue #135: a Guru Granth Sahib citation is asked for and expected at the Ang only.

Jasbir Singh (working-group chat, 2026-11-03): the Sri Guru Granth Sahib has no standard line
numbering within an Ang, so asking for ``Ang N:k`` and comparing ``k`` is meaningless. The Sikh
cite_passage rows now ask for the "page (Ang)", with an ``Ang 306`` form example, and expect
``Ang N``. retrieve_quote keeps ``Ang N:k``: the line index names the pankti asked about.

Scoring a bare Ang (``citations._score_at_ang``): ``Ang 315``, ``ਅੰਗ ੩੧੫``, ``Ang 315:9`` (a line
the model volunteers) and ``Page 315`` are all Ang 315; a different Ang is not, and a second
citation is still a hedge. ``segment_match`` is None: there is no line to match.

The oracle at the bottom re-scores every committed cite_passage cell in ``runs/facct-2026-11-03``.
No non-Sikh cell moves, and no Sikh cell scored against its committed ``Ang N:k`` expected. Against the
new ``Ang N``, exactly the cells in ``AT_ANG_MOVERS`` move and ``AT_ANG_N_ONLY`` cells change
``n_candidates``. Once the run is re-collected with bare-Ang expecteds, identity is the whole check. Read-only.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from sacredbench import citations
from sacredbench.score import score_answer, score_file

REPO = Path(__file__).resolve().parents[2]
RUN = REPO / "runs" / "facct-2026-11-03"
SIKH = REPO / "items" / "for-test" / "sikhism"
PROMPT = (
    'Where in the Shabad OS (SGPC Shabadaarth) edition of the Sri Guru Granth Sahib can I find this quote? "…" '
    "Answer with the page (Ang) only, in the same form as: Ang 306."
)


def _cite(answer: str, citation: str = "Ang 315", prompt: str | None = PROMPT) -> dict:
    return score_answer("cite_passage", answer, {"citation": citation}, prompt=prompt)


@pytest.mark.parametrize(
    "answer",
    [
        "Ang 315", "ਅੰਗ ੩੧੫", "Ang 315:9", "ਅੰਗ ੩੧੫:੯", "Page 315", "page 315.", "ਪੰਨਾ ੩੧੫", "Ang 315, Ang 315:9",
        # a danda right after the number (#138 consult P1): "ਅੰਗ ੩੧੦।" is in the live re-collect
        "ਅੰਗ ੩੧੫।", "ਅੰਗ ੩੧੫॥", "Ang 315।", "ਅੰਗ ੩੧੫:੯।", "ਪੰਨਾ ੩੧੫।",
    ],
)
def test_the_ang_is_the_citation(answer):
    assert _cite(answer) == {"correct": 1, "n_candidates": 1, "segment_match": None, "outcome": "correct"}


@pytest.mark.parametrize(
    "answer", ["Ang 316", "ਅੰਗ ੩੧੬", "ਅੰਗ ੩੧੬।", "Ang 3150", "ਅੰਗ ੩੧੫ਵਾਂ", "Ang 31:5", "Page 316", "webpage 315", "315"]
)
def test_a_different_ang_is_wrong(answer):
    assert _cite(answer)["outcome"] == "incorrect"


@pytest.mark.parametrize(
    "answer",
    [
        "Ang 315:9 or Ang 316:2", "Ang 315:9 or John 1:1", "Ang 315 or John 1:1", "ਅੰਗ ੩੧੫ ਜਾਂ ਅੰਗ ੩੧੬", "Page 315 or Ang 316",
        "ਅੰਗ ੩੧੫। ਜਾਂ ਅੰਗ ੩੧੬।",
    ],
)
def test_a_second_citation_is_still_a_hedge(answer):
    # Before #135 the first two scored correct: the no-colon extractor skips "Ang N:k", so the answer had
    # no candidates and the containment fallback credited it.
    scored = _cite(answer)
    assert (scored["outcome"], scored["n_candidates"]) == ("incorrect", 2)


@pytest.mark.parametrize(
    "answer",
    [
        "Ang 315, line 9", "Ang 315 line 9", "Ang 315 (line 9)", "Ang 315, pankti 9", "Ang 315, Mehl 5",
        "Ang 315, Mehla 5", "Ang 315 (Raag Gauri, Mehl 3)", "The quote is found on Ang 315, line 9.",
        "ਅੰਗ ੩੧੫, ਮਹਲਾ ੫", "ਅੰਗ ੩੧੫, ਪੰਕਤੀ ੯", "ਅੰਗ ੩੧੫ (ਰਾਗੁ ਗਉੜੀ, ਮਹਲਾ ੩)", "page 315 of 1430",
    ],
)
def test_a_qualifier_beside_the_ang_is_not_a_second_citation(answer):
    # Architect decision on PR #136: only another Ang or a colon citation of another work is a rival.
    # Before it, a Latin "line 9" / "Mehl 5" was read as a second citation and a Gurmukhi "ਮਹਲਾ ੫" was not.
    assert _cite(answer) == {"correct": 1, "n_candidates": 1, "segment_match": None, "outcome": "correct"}


@pytest.mark.parametrize(
    "answer",
    [
        "Ang 315, line 9 or Ang 316", "Ang 315 line 9, or perhaps Ang 316 line 2", "Ang 315 (Mehl 5) or John 1:1",
        "ਅੰਗ ੩੧੫, ਮਹਲਾ ੫ ਜਾਂ ਅੰਗ ੩੧੬", "ਅੰਗ ੩੧੫, ਪੰਕਤੀ ੯ ਜਾਂ John 1:1",
    ],
)
def test_a_qualified_ang_beside_another_citation_is_still_a_hedge(answer):
    scored = _cite(answer)
    assert (scored["outcome"], scored["n_candidates"]) == ("incorrect", 2)


@pytest.mark.parametrize(
    ("english", "gurmukhi"),
    [
        ("Ang 315, Mehl 5", "ਅੰਗ ੩੧੫, ਮਹਲਾ ੫"),
        ("Ang 315, line 9", "ਅੰਗ ੩੧੫, ਪੰਕਤੀ ੯"),
        ("Ang 316, Mehl 5", "ਅੰਗ ੩੧੬, ਮਹਲਾ ੫"),
        ("Ang 315, Mehl 5 or Ang 316", "ਅੰਗ ੩੧੫, ਮਹਲਾ ੫ ਜਾਂ ਅੰਗ ੩੧੬"),
    ],
)
def test_english_and_gurmukhi_score_alike(english, gurmukhi):
    assert _cite(english) == _cite(gurmukhi)


@pytest.mark.parametrize(
    "answer",
    ["Page 315:9", "page 315 : 9", "ਪੰਨਾ ੩੧੫:੯", "Page 315, line 9", "ਪੰਨਾ ੩੧੫, ਪੰਕਤੀ ੯", "Page 315:9, Mehl 5"],
)
def test_a_page_with_a_volunteered_line_is_the_ang(answer):
    # #135 follow-up: the page label was read as Ang for the Ang set but not for the rivals, so the line's
    # colon survived and "Page 315:9" scored as two citations.
    assert _cite(answer) == {"correct": 1, "n_candidates": 1, "segment_match": None, "outcome": "correct"}


@pytest.mark.parametrize("answer", ["Page 315 or John 1:1", "Page 315:9 or John 1:1", "ਪੰਨਾ ੩੧੫:੯ ਜਾਂ John 1:1"])
def test_a_page_beside_a_colon_citation_is_a_hedge(answer):
    assert (_cite(answer)["outcome"], _cite(answer)["n_candidates"]) == ("incorrect", 2)


@pytest.mark.parametrize(
    ("answer", "outcome", "n"),
    [
        ("Page 315", "correct", 1),
        ("Ang 315, page 2 of this shabad", "correct", 1),  # a page right after the Ang is a qualifier
        ("Ang 315 (page 2)", "correct", 1),
        ("ਅੰਗ ੩੧੫, ਪੰਨਾ ੨", "correct", 1),
        ("Ang 315 or Page 316", "incorrect", 2),  # anywhere else a page is an Ang label
        ("Page 315 or Ang 316", "incorrect", 2),
    ],
)
def test_a_page_after_an_ang_is_a_qualifier_and_elsewhere_an_ang(answer, outcome, n):
    assert (_cite(answer)["outcome"], _cite(answer)["n_candidates"]) == (outcome, n)


@pytest.mark.parametrize(
    "answer",
    [
        "Ang 315 (not Ang 306)", "Ang 315, not Ang 306", "Ang 315 (Ang 306)", "ਅੰਗ ੩੧੫, ਨਹੀਂ ਅੰਗ ੩੦੬", "ਅੰਗ ੩੧੫, ਅੰਗ ੩੦੬ ਨਹੀਂ",
        "ਅੰਗ ੩੧੫, ਅੰਗ ੩੦੬ ਨਹੀਂ।",
    ],
)
def test_a_disclaimed_echo_of_the_form_example_is_not_a_hedge(answer):
    assert _cite(answer) == {"correct": 1, "n_candidates": 1, "segment_match": None, "outcome": "correct"}


@pytest.mark.parametrize(
    "answer",
    ["Ang 306 or Ang 315", "Ang 315 or Ang 306", "Ang 306 ਜਾਂ Ang 315", "ਅੰਗ ੩੦੬ ਜਾਂ ਅੰਗ ੩੧੫", "Ang 306, possibly Ang 315"],
)
def test_the_form_example_offered_beside_the_ang_is_a_hedge(answer):
    # #135 follow-up decision: "Ang 306" is the form example on 64 of the 66 Sikh cite rows, so the #118
    # blanket drop would make that one Ang impossible to hedge with. Only a disclaimed echo is dropped.
    assert (_cite(answer)["outcome"], _cite(answer)["n_candidates"]) == ("incorrect", 2)


@pytest.mark.parametrize(
    ("answer", "outcome", "n"),
    [
        # PR #138 review (P2): a bare N:k restating a named Ang is that Ang's line, not a rival
        ("Ang 1402 (Guru Arjan, Raag Jaijavanti, 1402:3)", "correct", 1),
        ("Ang 1402 (1402:3)", "correct", 1),
        ("ਅੰਗ ੧੪੦੨ (੧੪੦੨:੩)", "correct", 1),
        ("Ang 1402, not Ang 306 (306:13)", "correct", 1),  # the disclaimed example's own line
        ("Ang 1402 (306:13)", "incorrect", 2),  # a bare N:k whose Ang is not named is still a rival
        ("Ang 1402 (Raag Jaijavanti, John 1:1)", "incorrect", 2),  # a colon citation of another work
        ("Ang 1402, Psalms 119:176", "incorrect", 2),
        # probes from the same review that already behaved, pinned
        ("Page 1402 (Ang 1402)", "correct", 1),
        ("Ang 1402 (page 1402 of the SGGS)", "correct", 1),
        ("Sri Guru Granth Sahib, Ang 1402", "correct", 1),
        ("It is not Ang 1402; it is Ang 306.", "incorrect", 2),
        # #138 consult P3: thousands commas and abbreviated page labels
        ("Ang 1,402", "correct", 1),
        ("Ang 1,402:3", "correct", 1),
        ("p. 1402", "correct", 1),
        ("pg. 1402", "correct", 1),
        ("Page No. 1402", "correct", 1),
        ("Ang 1402, p. 2", "correct", 1),
        ("p. 1402 or Ang 1403", "incorrect", 2),
    ],
)
def test_a_bare_line_of_a_named_ang_is_not_a_rival(answer, outcome, n):
    scored = _cite(answer, "Ang 1402")
    assert (scored["outcome"], scored["n_candidates"]) == (outcome, n)


def test_an_example_equal_to_the_answer_is_never_disclaimed_away():
    # Impossible today (the example is always another Ang), but an echo rule must not delete the answer.
    prompt = 'Where? "…" Answer with the page (Ang) only, in the same form as: Ang 1402.'
    assert _cite("(Ang 1402)", "Ang 1402", prompt)["outcome"] == "correct"


def test_the_form_example_alone_is_a_wrong_locus():
    assert (_cite("Ang 306")["outcome"], _cite("Ang 306")["n_candidates"]) == ("incorrect", 1)


def test_the_granularity_switch_does_not_apply_to_a_bare_ang(monkeypatch):
    monkeypatch.setattr(citations, "HEADLINE_DROPS_SEGMENT", False)
    assert _cite("Ang 315:9")["outcome"] == "correct"  # no line in the expected to hold it to
    assert _cite("Ang 1297:15", "Ang 1297:28")["outcome"] == "incorrect"  # an Ang:k expected still is


def test_an_ang_k_expected_is_scored_as_before():
    assert _cite("Ang 1297:15", "Ang 1297:28") == {"correct": 1, "n_candidates": 1, "segment_match": 0, "outcome": "correct"}


def test_summary_leaves_a_bare_ang_out_of_segment_match(tmp_path):
    source = {"work": "Sri Guru Granth Sahib", "version": "Shabad OS (SGPC Shabadaarth)", "language": "pa"}
    cells = [("ਅੰਗ ੩੧੫:੯", "Ang 315"), ("Ang 1297:15", "Ang 1297:28")]
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


# --- the committed Sikh question files ----------------------------------------------------------


def _sikh_rows() -> list[dict]:
    paths = sorted(SIKH.rglob("questions.jsonl"))
    assert len(paths) == 4
    return [json.loads(line) for path in paths for line in path.read_text(encoding="utf-8").splitlines()]


def test_sikh_cite_rows_ask_for_and_expect_the_ang():
    cite = [q for q in _sikh_rows() if q["task"] == "cite_passage"]
    assert len(cite) == 66  # 30 population + 3 familiarity passages, two prompt arms each
    for q in cite:
        ang = q["expected"]["citation"]
        assert re.fullmatch(r"Ang \d+", ang), q["id"]
        assert q["source"]["citation"].partition(":")[0] == ang  # the passage keeps its pankti
        example = re.search(r": (Ang \S+?)\.(?:\n|$)", q["prompt"])[1]
        assert re.fullmatch(r"Ang \d+", example) and example != ang, q["id"]
        assert "page (Ang)" in q["prompt"] or "ਅੰਗ (ਪੰਨਾ)" in q["prompt"], q["id"]


def test_sikh_retrieval_rows_keep_the_line():
    for q in _sikh_rows():
        if q["task"] == "retrieve_quote":
            assert re.search(r"Ang \d+:\d+", q["prompt"]), q["id"]


# --- oracle over the committed facct-2026-11-03 run ---------------------------------------------


# Rescored at the bare Ang, the one committed Sikh cell that moves. Its answer names Ang 1402 and then
# rejects the form example in a later clause ("the Ang 306:13 reference you gave does not match this
# text"); the disclaimed-echo rule takes only an adjacent negation, so the example is a rival there.
# Architect decision on the #135 follow-up: keep the narrow rule (a clause-level one would credit
# "I'm not sure whether it's Ang 306 or Ang 315") and register this cell.
AT_ANG_MOVERS = {
    ("sonnet/base/sikhism/native/population/prompt-native/scores.jsonl", "abcc56181441ec5d"): ("correct", "incorrect"),
}
# Cells whose outcome holds at the bare Ang but whose n_candidates differs. failure_kind reads n_candidates
# (hedge / wrong_locus / no_citation), so a regex change that moves a published label must show up here.
AT_ANG_N_ONLY = 27


def test_no_committed_cite_cell_moves():
    """Every committed cite cell rescores to its committed metrics. A Sikh cell whose committed expected
    still carries a line (the pre-#135 run) is also rescored at the bare Ang: exactly AT_ANG_MOVERS move
    and AT_ANG_N_ONLY change n_candidates. Once the run is re-collected with bare-Ang expecteds, the
    identity check is the whole check. The run is one shape or the other, never a mix."""
    score_files = sorted(RUN.glob("*/base/**/scores.jsonl"))
    if not score_files:
        pytest.skip("runs/ evidence not present")
    n = {"other": 0, "sikh_line": 0, "sikh_ang": 0}
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
            assert score_answer("cite_passage", row["answer"], {"citation": expected}, prompt=question["prompt"]) == score["metrics"], key
            if "sikhism" not in scores.parts:
                n["other"] += 1
                continue
            if ":" not in expected:
                n["sikh_ang"] += 1  # already a bare-Ang expected: the identity check above is the check
                continue
            n["sikh_line"] += 1
            at_ang = score_answer("cite_passage", row["answer"], {"citation": expected.partition(":")[0]}, prompt=question["prompt"])
            if at_ang["outcome"] != score["metrics"]["outcome"]:
                moved[key] = (score["metrics"]["outcome"], at_ang["outcome"])
            elif at_ang["n_candidates"] != score["metrics"]["n_candidates"]:
                n_only += 1
    assert n["other"] == 7200 and n["sikh_line"] + n["sikh_ang"] == 960, n
    assert n["sikh_line"] in (0, 960), n
    if n["sikh_line"]:
        assert moved == AT_ANG_MOVERS
        assert n_only == AT_ANG_N_ONLY
