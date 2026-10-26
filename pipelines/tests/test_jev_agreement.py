"""Agreement report (Spec 21 phase 4): join + confusion + raw distribution + disagreement enumeration.
Fixture-based, no network, no run artifacts touched."""
from __future__ import annotations

import pytest

from sacredbench.jev import answer_digest
from sacredbench.jev_agreement import (
    AgreementError,
    agreement,
    join_cells,
    render_markdown,
)


def _triple(qid, mid, *, contains_reference, outcome, token_f1, matches_requested_p, refusal_p,
            answer="ans", expected="exp"):
    """Build the (answer, score, judgment) rows for one retrieve_quote cell."""
    answer_row = {"question_id": qid, "model_id": mid, "task": "retrieve_quote", "answer": answer,
                  "question": {"expected": {"text": expected}}}
    score_row = {"question_id": qid, "model_id": mid, "task": "retrieve_quote",
                 "metrics": {"contains_reference": contains_reference, "outcome": outcome,
                             "token_f1": token_f1, "correct": int(outcome == "correct")}}
    judgment_row = {"question_id": qid, "model_id": mid, "rubric_id": "sacredbench-jev-1",
                    "matches_requested_p": matches_requested_p, "refusal_p": refusal_p,
                    "equivalence": "not_evaluated", "answer_digest": answer_digest(answer)}
    return answer_row, score_row, judgment_row


# A agree/agree · B containment judge-only · C agree/agree · D containment det-only + refusal judge-only
_SPECS = [
    ("q-A", "m", dict(contains_reference=1, outcome="correct", token_f1=1.0, matches_requested_p=0.9, refusal_p=0.02)),
    ("q-B", "m", dict(contains_reference=0, outcome="incorrect", token_f1=0.85, matches_requested_p=0.8, refusal_p=0.1)),
    ("q-C", "m", dict(contains_reference=0, outcome="refused", token_f1=0.0, matches_requested_p=0.1, refusal_p=0.97)),
    ("q-D", "m", dict(contains_reference=1, outcome="correct", token_f1=0.95, matches_requested_p=0.3, refusal_p=0.6)),
]


def _streams(specs=_SPECS):
    answers, scores, judgments = [], [], []
    for qid, mid, kw in specs:
        a, s, j = _triple(qid, mid, **kw)
        answers.append(a); scores.append(s); judgments.append(j)
    return answers, scores, judgments


def test_join_is_complete_and_keyed_on_qid_model():
    cells = join_cells(*_streams())
    assert len(cells) == 4
    by = {(c["question_id"], c["model_id"]): c for c in cells}
    assert by[("q-A", "m")]["expected_text"] == "exp" and by[("q-A", "m")]["contains_reference"] == 1
    assert by[("q-B", "m")]["matches_requested_p"] == 0.8


def test_join_fails_fast_on_judgment_without_score():
    answers, scores, judgments = _streams()
    scores.pop()  # drop q-D's score, keep its judgment
    with pytest.raises(AgreementError, match="no matching score"):
        join_cells(answers, scores, judgments)


def test_containment_and_refusal_confusion_counts():
    rep = agreement(join_cells(*_streams()))
    cc = rep["containment"]["confusion"]
    assert (cc["both"], cc["judge_only"], cc["deterministic_only"], cc["neither"]) == (1, 1, 1, 1)
    assert cc["agree"] == 2 and cc["agreement_rate"] == 0.5
    rc = rep["refusal"]["confusion"]
    assert (rc["both"], rc["judge_only"], rc["deterministic_only"], rc["neither"]) == (1, 1, 0, 2)
    assert rc["agree"] == 3 and rc["agreement_rate"] == 0.75


def test_disagreements_are_exhaustive_and_labeled():
    rep = agreement(join_cells(*_streams()))
    assert rep["n_disagreements"] == 2
    by = {d["question_id"]: d for d in rep["disagreements"]}
    assert by["q-B"]["disagree_on"] == ["containment"]
    assert set(by["q-D"]["disagree_on"]) == {"containment", "refusal"}  # both axes
    # the disagreement carries the manual-review context (expected + answer + token_f1)
    assert by["q-B"]["token_f1"] == 0.85 and by["q-B"]["expected_text"] == "exp"


def test_threshold_is_inclusive_at_0_5():
    # p exactly 0.5 counts as the judge asserting the verdict (>= THRESHOLD)
    a, s, j = _triple("q-E", "m", contains_reference=0, outcome="incorrect", token_f1=0.5,
                      matches_requested_p=0.5, refusal_p=0.5)
    rep = agreement(join_cells([a], [s], [j]))
    # judge contains (0.5>=0.5) vs det not-contains → containment disagreement; judge refusal (0.5>=0.5)
    # vs det not-refused → refusal disagreement
    assert rep["n_disagreements"] == 1
    assert set(rep["disagreements"][0]["disagree_on"]) == {"containment", "refusal"}


def test_raw_distribution_split_by_deterministic_class():
    rep = agreement(join_cells(*_streams()))
    cont = rep["containment"]["judge_prob_by_deterministic_class"]
    # contains_reference=1 cells are q-A (0.9) and q-D (0.3) → mean 0.6, n 2
    assert cont["contains_reference=1"]["n"] == 2 and cont["contains_reference=1"]["mean"] == 0.6
    # contains_reference=0 cells are q-B (0.8) and q-C (0.1) → n 2
    assert cont["contains_reference=0"]["n"] == 2
    # histogram bins sum to n
    hist = cont["contains_reference=1"]["histogram"]
    assert sum(hist.values()) == 2


def test_agreement_fails_fast_on_bad_probability():
    a, s, j = _triple("q-X", "m", contains_reference=0, outcome="incorrect", token_f1=0.0,
                      matches_requested_p=1.4, refusal_p=0.1)  # p out of [0,1]
    with pytest.raises(AgreementError, match="not a probability"):
        agreement(join_cells([a], [s], [j]))


def test_render_markdown_contains_sections():
    md = render_markdown(agreement(join_cells(*_streams())))
    assert "# Jev agreement report" in md
    assert "## Containment" in md and "## Refusal" in md
    assert "## Disagreements (2)" in md
    assert "q-D × m" in md  # the double-axis disagreement is enumerated


def test_join_cross_checks_answer_digest():
    # self-verifying: a judgment's answer_digest must match the joined answer (claude phase-4 #3)
    a, s, j = _triple("q-A", "m", contains_reference=1, outcome="correct", token_f1=1.0,
                      matches_requested_p=0.9, refusal_p=0.02, answer="hello")
    ok = join_cells([a], [s], [dict(j, answer_digest=answer_digest("hello"))])
    assert len(ok) == 1
    with pytest.raises(AgreementError, match="answer_digest"):
        join_cells([a], [s], [dict(j, answer_digest=answer_digest("a different answer"))])


def test_judge_agreement_cli_writes_reports(tmp_path):
    import json as _json
    from typer.testing import CliRunner
    from sacredbench.cli import app

    answers, scores, judgments = _streams()
    # give the judgments real answer_digests so the self-verify check passes end-to-end
    for a, j in zip(answers, judgments):
        j["answer_digest"] = answer_digest(a["answer"])
    (tmp_path / "a.jsonl").write_text("\n".join(_json.dumps(r) for r in answers) + "\n")
    (tmp_path / "s.jsonl").write_text("\n".join(_json.dumps(r) for r in scores) + "\n")
    (tmp_path / "j.jsonl").write_text("\n".join(_json.dumps(r) for r in judgments) + "\n")
    r = CliRunner().invoke(app, ["judge-agreement", str(tmp_path / "a.jsonl"), str(tmp_path / "s.jsonl"),
                                 str(tmp_path / "j.jsonl"), "--json-out", str(tmp_path / "ag.json"),
                                 "--md-out", str(tmp_path / "ag.md")])
    assert r.exit_code == 0, r.output
    assert "## Disagreements (2)" in r.output
    report = _json.loads((tmp_path / "ag.json").read_text())
    assert report["n_cells"] == 4 and report["n_disagreements"] == 2
    assert (tmp_path / "ag.md").exists()


# ---- PR #47 round-1: the join is strict + self-verifying ----

def test_join_fails_fast_on_missing_answer():
    answers, scores, judgments = _streams()
    answers.pop()  # drop q-D's answer
    with pytest.raises(AgreementError, match="no matching answer"):
        join_cells(answers, scores, judgments)


def test_join_fails_fast_on_missing_answer_digest():
    a, s, j = _triple("q-A", "m", contains_reference=1, outcome="correct", token_f1=1.0,
                      matches_requested_p=0.9, refusal_p=0.02)
    del j["answer_digest"]
    with pytest.raises(AgreementError, match="no answer_digest"):
        join_cells([a], [s], [j])


def test_join_fails_fast_on_duplicate_judgment():
    a, s, j = _triple("q-A", "m", contains_reference=1, outcome="correct", token_f1=1.0,
                      matches_requested_p=0.9, refusal_p=0.02)
    with pytest.raises(AgreementError, match="duplicate judgment"):
        join_cells([a, a], [s, s], [j, j])
