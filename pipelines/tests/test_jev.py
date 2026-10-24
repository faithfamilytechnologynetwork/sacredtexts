"""Jev judgments (Spec 21). The Decisions API is injected; no network and no key.

The fail-fast parser is pinned to a committed, redacted *live* Decisions response
(``testdata/jev_decision_sample.json``) so the shape under test is the real wire
shape, not a hand-written mock (project lesson: mocking the provider seam hides
live-only failures).
"""

import json
from pathlib import Path

import pytest

from sacredbench.jev import (
    JEV_MODEL,
    JevError,
    answer_digest,
    estimate,
    interpret,
    judge,
    summarize,
)

FIXTURE = Path(__file__).parent / "testdata" / "jev_decision_sample.json"


def _live_payload() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _payload(refusal=0.1, matches=0.2, build="typesafe/jev-1.14-20261014", kind=None):
    p = {
        "id": "gen-dec-1",
        "model": build,
        "provider": "TypeSafe",
        "answers": {
            "refusal": {"type": "noul", "noul": refusal},
            "matches_requested": {"type": "noul", "noul": matches},
        },
        "usage": {"input_tokens": 12, "output_tokens": 0, "cost": 0.000001},
    }
    if kind is not None:
        p["answers"]["kind"] = {"type": "choice", "choice": kind,
                                "probabilities": {kind: 0.8}, "confidence": 0.7}
    return p


def _row(answer="some other sentence entirely", task="retrieve_quote",
         work="The Bible", version="KJV", language="en",
         qid="retrieve_quote-aaaa", model_id="m1", qsd=None):
    row = {
        "question_id": qid,
        "model_id": model_id,
        "model": "google/gemma-3-4b-it",
        "task": task,
        "answer": answer,
        "question": {
            "expected": {"text": "the requested line of scripture here"},
            "source": {"tradition": ["Protestant Christian"], "work": work,
                       "version": version, "language": language, "citation": "Isaiah 1:1"},
        },
    }
    if qsd is not None:
        row["question_set_digest"] = qsd
    return row


# ---- interpret / fixture -------------------------------------------------

def test_interpret_two_questions_records_not_evaluated():
    parsed = interpret(_payload(refusal=0.9, matches=0.1), with_equivalence=False)
    assert parsed["refusal_p"] == 0.9
    assert parsed["matches_requested_p"] == 0.1
    assert parsed["equivalence"] == "not_evaluated"
    assert parsed["judge_model_resolved"] == "typesafe/jev-1.14-20261014"
    assert parsed["usage"]["cost"] == 0.000001


def test_interpret_equivalence_reads_the_live_fixture_shape():
    parsed = interpret(_live_payload(), with_equivalence=True)
    assert parsed["matches_requested_p"] == 0.97
    assert parsed["equivalence"]["kind"] == "requested_wording"
    assert parsed["equivalence"]["confidence"] == 0.97
    assert parsed["judge_model_resolved"] == "typesafe/jev-1.14-20261014"


def test_interpret_fails_fast_on_bad_shapes():
    with pytest.raises(JevError, match="answers"):
        interpret({"no": "answers"}, with_equivalence=False)
    bad = _payload()
    bad["answers"]["refusal"] = {"type": "choice", "choice": "x"}
    with pytest.raises(JevError, match="refusal"):
        interpret(bad, with_equivalence=False)
    bad2 = _payload(kind="maybe")
    with pytest.raises(JevError, match="kind"):
        interpret(bad2, with_equivalence=True)
    nobuild = _payload()
    nobuild["model"] = None
    with pytest.raises(JevError, match="resolved model build"):
        interpret(nobuild, with_equivalence=False)


# ---- judge pass ----------------------------------------------------------

def test_judge_is_resumable_records_build_and_digest(tmp_path):
    out = tmp_path / "judgments.jsonl"
    calls = {"n": 0}

    def decide(state):
        calls["n"] += 1
        return _payload(refusal=0.9)

    row = _row(answer="I'm sorry, I can't provide that.")
    done, failed, _ = judge([row], out, decide=decide, concurrency=1)
    assert (done, failed) == (1, 0)
    written = json.loads(out.read_text().splitlines()[0])
    assert written["judge_model"] == JEV_MODEL
    assert written["judge_model_resolved"] == "typesafe/jev-1.14-20261014"
    assert written["answer_digest"] == answer_digest("I'm sorry, I can't provide that.")
    assert written["equivalence"] == "not_evaluated"
    # manifest records the resolved build identity
    manifest = json.loads((tmp_path / "judgments.jsonl.manifest.json").read_text())
    assert manifest["judge_model_resolved"] == "typesafe/jev-1.14-20261014"
    assert manifest["rubric_id"] == written["rubric_id"]

    # resume: nothing new, no decider calls
    done2, failed2, _ = judge([row], out, decide=decide, concurrency=1)
    assert (done2, failed2) == (0, 0)
    assert calls["n"] == 1
    assert len(out.read_text().splitlines()) == 1


def test_changed_answer_is_rejudged(tmp_path):
    out = tmp_path / "j.jsonl"
    judge([_row(answer="first answer")], out, decide=lambda s: _payload(), concurrency=1)
    # same question_id/model_id but a different answer → different digest → pending again
    judge([_row(answer="a totally different answer")], out, decide=lambda s: _payload(), concurrency=1)
    assert len(out.read_text().splitlines()) == 2


def test_build_mismatch_on_resume_fails_fast(tmp_path):
    out = tmp_path / "j.jsonl"
    judge([_row(answer="A", qid="q-A")], out, decide=lambda s: _payload(build="buildX"), concurrency=1)
    # a new pending cell whose live build differs from the pinned one
    with pytest.raises(JevError, match="build"):
        judge([_row(answer="B", qid="q-B")], out, decide=lambda s: _payload(build="buildY"), concurrency=1)


def test_task_filter_skips_non_text_retrieval(tmp_path):
    out = tmp_path / "j.jsonl"
    calls = {"n": 0}

    def decide(state):
        calls["n"] += 1
        return _payload()

    done, failed, _ = judge([_row(task="verify_source")], out, decide=decide, concurrency=1)
    assert (done, failed, calls["n"]) == (0, 0, 0)
    assert not out.exists() or out.read_text() == ""


def test_restricted_source_is_never_judged(tmp_path):
    out = tmp_path / "j.jsonl"
    calls = {"n": 0}

    def decide(state):
        calls["n"] += 1
        return _payload()

    restricted = frozenset({("The Bible", "NABRE", "en")})
    done, _, _ = judge([_row(version="NABRE")], out, decide=decide, concurrency=1,
                       restricted_keys=restricted)
    assert done == 0 and calls["n"] == 0


def test_missing_credential_fails_fast_before_any_call(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with pytest.raises(JevError, match="OPENROUTER_API_KEY"):
        judge([_row()], tmp_path / "j.jsonl")


def test_failed_cell_is_not_written(tmp_path):
    out = tmp_path / "j.jsonl"

    def decide(state):
        raise JevError("decisions API 500: no")

    done, failed, messages = judge([_row()], out, decide=decide, concurrency=1)
    assert (done, failed) == (0, 1) and "500" in messages[0]
    assert not out.exists() or out.read_text() == ""


# ---- estimate / summarize ------------------------------------------------

def test_estimate_counts_pending_and_spend(tmp_path):
    out = tmp_path / "j.jsonl"
    rows = [_row(qid="q1"), _row(qid="q2", task="verify_source"),
            _row(qid="q3", version="NABRE")]
    est = estimate(rows, out, restricted_keys=frozenset({("The Bible", "NABRE", "en")}))
    assert est["pending"] == 1
    assert est["skipped_task"] == 1
    assert est["skipped_restricted"] == 1
    assert est["estimated_usd"] > 0


def test_summarize_is_a_noop_over_a_finished_file(tmp_path):
    out = tmp_path / "j.jsonl"
    judge([_row(answer="declines", qid="q1")], out, decide=lambda s: _payload(refusal=0.9), concurrency=1)
    s = summarize(out)
    assert s["n"] == 1
    assert s["judge_models"] == ["typesafe/jev-1.14-20261014"]
    assert s["kinds"]["not_evaluated"] == 1
    assert s["rubric_id"] == "sacredbench-jev-1"


# ---- the judge is never on the default scoring path ----------------------

def test_score_and_collect_do_not_invoke_the_judge():
    import sacredbench.collect as collect
    import sacredbench.score as score
    for mod in (score, collect):
        src = Path(mod.__file__).read_text(encoding="utf-8")
        assert "jev" not in src.lower(), f"{mod.__name__} references the judge"
