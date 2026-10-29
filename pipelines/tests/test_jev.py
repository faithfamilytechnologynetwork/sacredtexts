"""Jev judgments (Spec 21). The Decisions API is injected; no network and no key.

The fail-fast parser is pinned to a committed, redacted *live* Decisions response
(``testdata/jev_decision_sample.json``) so the shape under test is the real wire
shape, not a hand-written mock (project lesson: mocking the provider seam hides
live-only failures).
"""

import hashlib
import json
import re
from pathlib import Path

import pytest

from sacredbench.jev import (
    JEV_MODEL,
    EquivalenceIndex,
    JevError,
    answer_digest,
    estimate,
    interpret,
    judge,
    load_equivalence_index,
    summarize,
)

FIXTURE = Path(__file__).parent / "testdata" / "jev_decision_sample.json"
INDEX_FIXTURE = Path(__file__).parent / "testdata" / "equivalence_index.sample.jsonl"
INDEX_CORPUS_HASH = "testcorpus-ed3f05dcf703"  # matches the fixture manifest's corpus_hash


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
        # a full choice distribution over all kinds (the live API returns every label), the chosen
        # one carrying the mass — interpret() now validates all labels are present + in [0,1]
        probs = {k: 0.0 for k in ("refusal", "requested_wording", "other_indexed_wording", "neither")}
        probs[kind] = 0.8
        p["answers"]["kind"] = {"type": "choice", "choice": kind,
                                "probabilities": probs, "confidence": 0.7}
    return p


def _row(answer="some other sentence entirely", task="retrieve_quote",
         work="The Bible", version="KJV", language="en",
         qid="retrieve_quote-aaaa", model_id="m1", qsd="qs-digest-1"):
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
    assert parsed["kind"] == "requested_wording"          # flat, matching the spec schema
    assert parsed["kind_confidence"] == 0.97
    assert "equivalence" not in parsed
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


def test_interpret_fails_loud_on_mistyped_or_missing_fields():
    # non-numeric noul
    s = _payload()
    s["answers"]["refusal"]["noul"] = "high"
    with pytest.raises(JevError, match="probability"):
        interpret(s, with_equivalence=False)
    # bool is not a number
    s = _payload()
    s["answers"]["matches_requested"]["noul"] = True
    with pytest.raises(JevError, match="probability"):
        interpret(s, with_equivalence=False)
    # missing usage → budget would read zero
    s = _payload()
    del s["usage"]
    with pytest.raises(JevError, match="usage"):
        interpret(s, with_equivalence=False)
    # non-numeric cost
    s = _payload()
    s["usage"]["cost"] = None
    with pytest.raises(JevError, match="cost"):
        interpret(s, with_equivalence=False)
    # missing decision id / provider
    s = _payload()
    s["id"] = None
    with pytest.raises(JevError, match="decision id"):
        interpret(s, with_equivalence=False)
    s = _payload()
    s["provider"] = ""
    with pytest.raises(JevError, match="provider"):
        interpret(s, with_equivalence=False)
    # equivalence on, but probabilities/confidence malformed
    s = _payload(kind="neither")
    s["answers"]["kind"]["confidence"] = "high"
    with pytest.raises(JevError, match="confidence"):
        interpret(s, with_equivalence=True)


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


def test_concurrent_build_conflict_fails_fast(tmp_path):
    """With >1 worker, whichever cell pins the build first, a differing in-flight build conflicts."""
    out = tmp_path / "j.jsonl"
    from itertools import count
    from threading import Lock
    lock = Lock()
    counter = count()

    def decide(state):
        with lock:
            i = next(counter)
        return _payload(build=f"build-{i % 2}")  # alternates build-0 / build-1

    rows = [_row(answer=f"ans{i}", qid=f"q{i}") for i in range(4)]
    with pytest.raises(JevError, match="conflict|build"):
        judge(rows, out, decide=decide, concurrency=4)


def test_existing_row_build_mismatch_on_resume_fails_fast(tmp_path):
    """A manifest pinned to build X beside a row from build Y (a hand-edited or half-written
    file) is a mixed-build file; resume must refuse it, not trust the row and extend it."""
    out = tmp_path / "j.jsonl"
    # Write one clean row + manifest pinned to buildX.
    judge([_row(answer="A", qid="q-A")], out, decide=lambda s: _payload(build="buildX"), concurrency=1)
    # Corrupt the file: append a row that claims a different build.
    rogue = json.loads(out.read_text().splitlines()[0])
    rogue["question_id"] = "q-B"
    rogue["judge_model_resolved"] = "buildY"
    with out.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rogue) + "\n")
    # Any resume (even just estimating) now fails fast on the build disagreement.
    with pytest.raises(JevError, match="build"):
        estimate([_row(qid="q-C")], out)
    with pytest.raises(JevError, match="build"):
        judge([_row(qid="q-C")], out, decide=lambda s: _payload(build="buildX"), concurrency=1)


def test_existing_row_without_build_on_resume_fails_fast(tmp_path):
    out = tmp_path / "j.jsonl"
    judge([_row(answer="A", qid="q-A")], out, decide=lambda s: _payload(build="buildX"), concurrency=1)
    row = json.loads(out.read_text().splitlines()[0])
    del row["judge_model_resolved"]
    row["question_id"] = "q-B"
    with out.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")
    with pytest.raises(JevError, match="judge_model_resolved"):
        estimate([_row(qid="q-C")], out)


def test_manifest_without_build_fails_fast(tmp_path):
    """A hand-edited manifest missing the resolved build would let the next response re-pin it —
    the same mixed-build hole closed for the no-manifest case. Refuse up front."""
    out = tmp_path / "j.jsonl"
    judge([_row(answer="A", qid="q-A")], out, decide=lambda s: _payload(build="buildX"), concurrency=1)
    mpath = tmp_path / "j.jsonl.manifest.json"
    manifest = json.loads(mpath.read_text())
    del manifest["judge_model_resolved"]
    mpath.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(JevError, match="judge_model_resolved"):
        estimate([_row(qid="q-B")], out)


def test_mixed_question_set_digest_presence_fails_fast(tmp_path):
    out = tmp_path / "j.jsonl"
    rows = [_row(qid="q1", qsd="deadbeef"), _row(qid="q2", qsd=None)]  # one with a digest, one without
    with pytest.raises(JevError, match="with and without a question_set_digest"):
        estimate(rows, out)


def test_existing_row_question_set_digest_mismatch_fails_fast(tmp_path):
    """A row with the same question/model/answer but a different question-set digest must NOT be
    treated as a completed cell of the current set (the resume key omits the digest)."""
    out = tmp_path / "j.jsonl"
    judge([_row(answer="A", qid="q-A", qsd="digestA")], out,
          decide=lambda s: _payload(), concurrency=1, question_set_digest="digestA")
    # Corrupt: append a row that claims a different question set.
    rogue = json.loads(out.read_text().splitlines()[0])
    rogue["question_id"] = "q-B"
    rogue["question_set_digest"] = "digestB"
    with out.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rogue) + "\n")
    with pytest.raises(JevError, match="question-set digest"):
        estimate([_row(qid="q-C", qsd="digestA")], out, question_set_digest="digestA")


def test_negative_limit_fails_fast_before_any_call(tmp_path):
    """A negative cap would judge all-but-|limit| cells — the opposite of a budget guard."""
    out = tmp_path / "j.jsonl"
    rows = [_row(answer=f"a{i}", qid=f"q{i}") for i in range(3)]
    with pytest.raises(JevError, match="limit"):
        estimate(rows, out, limit=-1)
    calls = {"n": 0}

    def decide(state):
        calls["n"] += 1
        return _payload()

    with pytest.raises(JevError, match="limit"):
        judge(rows, out, decide=decide, concurrency=1, limit=-1)
    assert calls["n"] == 0  # rejected before any decision call
    assert not out.exists() or out.read_text() == ""


def test_summarize_on_truncated_file_fails_fast(tmp_path):
    out = tmp_path / "j.jsonl"
    judge([_row(answer="A", qid="q-A")], out, decide=lambda s: _payload(), concurrency=1)
    with out.open("a", encoding="utf-8") as fh:
        fh.write('{"truncated": ')  # a half-written final line (the interrupt case)
    with pytest.raises(JevError, match="not JSON"):
        summarize(out)


def test_nonempty_sidecar_without_manifest_fails_fast(tmp_path):
    out = tmp_path / "j.jsonl"
    out.write_text(json.dumps({"rubric_id": "sacredbench-jev-1", "question_id": "q",
                               "model_id": "m", "answer_digest": "x"}) + "\n", encoding="utf-8")
    # no manifest beside it → unknown build identity → refuse
    with pytest.raises(JevError, match="manifest"):
        estimate([_row()], out)
    with pytest.raises(JevError, match="manifest"):
        judge([_row()], out, decide=lambda s: _payload())


def test_limit_caps_cells_judged(tmp_path):
    out = tmp_path / "j.jsonl"
    rows = [_row(answer=f"a{i}", qid=f"q{i}") for i in range(3)]
    est = estimate(rows, out, limit=1)
    assert est["pending"] == 1
    done, failed, _ = judge(rows, out, decide=lambda s: _payload(), concurrency=1, limit=1)
    assert done == 1
    assert len(out.read_text().splitlines()) == 1


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


def test_summarize_is_a_noop_over_a_finished_file_and_sums_cost(tmp_path):
    out = tmp_path / "j.jsonl"
    rows = [_row(answer="declines", qid="q1"), _row(answer="and another", qid="q2")]
    judge(rows, out, decide=lambda s: _payload(refusal=0.9), concurrency=1)
    s = summarize(out)
    assert s["n"] == 2
    assert s["judge_models"] == ["typesafe/jev-1.14-20261014"]
    assert s["kinds"]["not_evaluated"] == 2
    assert s["refusal_p_ge_0.5"] == 2
    # each _payload() reports cost 0.000001 → total surfaced
    assert s["total_cost_usd"] == pytest.approx(0.000002)
    assert s["rubric_id"] == "sacredbench-jev-1"


# ---- the judge is never on the default scoring path ----------------------

# ---- CLI: the --yes budget gate and missing-path guards ------------------

def _answers_file(tmp_path):
    answers = tmp_path / "answers.jsonl"
    answers.write_text(json.dumps(_row(qid="q1")) + "\n", encoding="utf-8")
    return answers


def test_cli_judge_without_yes_refuses_to_spend(tmp_path, monkeypatch):
    """The --yes gate is the single enforcement point for 'no unseen live pass' and the $8 cap:
    without it, the paid pass never starts."""
    from typer.testing import CliRunner

    import sacredbench.cli as climod
    from sacredbench import jev as jevmod
    from sacredbench.cli import app

    monkeypatch.setattr(climod, "_require_catalogue", lambda root: [])
    monkeypatch.setattr(climod.aud, "restricted_keys", lambda sources: set())
    called = {"judge": False}

    def _boom(*a, **k):
        called["judge"] = True
        raise AssertionError("jev.judge must not run without --yes")

    monkeypatch.setattr(jevmod, "judge", _boom)

    answers = _answers_file(tmp_path)
    out = tmp_path / "j.jsonl"
    r = CliRunner().invoke(app, ["judge", str(answers), "--out", str(out)])
    assert r.exit_code == 2
    assert "re-run with --yes" in r.output
    assert called["judge"] is False
    assert not out.exists()  # nothing paid, nothing written


def test_cli_judge_missing_answers_file_is_a_clean_error(tmp_path, monkeypatch):
    from typer.testing import CliRunner

    import sacredbench.cli as climod
    from sacredbench.cli import app

    monkeypatch.setattr(climod, "_require_catalogue", lambda root: [])
    r = CliRunner().invoke(app, ["judge", str(tmp_path / "nope.jsonl"), "--out", str(tmp_path / "j.jsonl")])
    assert r.exit_code != 0
    assert "input path not found" in r.output


def test_cli_judge_summary_missing_sidecar_is_a_clean_error(tmp_path):
    from typer.testing import CliRunner

    from sacredbench.cli import app

    r = CliRunner().invoke(app, ["judge-summary", str(tmp_path / "nope.jsonl")])
    assert r.exit_code != 0
    assert "sidecar not found" in r.output


def test_cli_judge_corrupt_answers_is_a_clean_error(tmp_path, monkeypatch):
    from typer.testing import CliRunner

    import sacredbench.cli as climod
    from sacredbench.cli import app

    monkeypatch.setattr(climod, "_require_catalogue", lambda root: [])
    answers = tmp_path / "answers.jsonl"
    answers.write_text("{not json\n", encoding="utf-8")
    r = CliRunner().invoke(app, ["judge", str(answers), "--out", str(tmp_path / "j.jsonl")])
    assert r.exit_code != 0
    assert "not valid JSONL" in r.output


# ---- the judge is never on the default scoring path ----------------------

def test_score_and_collect_do_not_invoke_the_judge():
    # The judge is paid and must never run from the default scoring/collection path. Assert the
    # *invocation* surfaces are absent (not merely the word "jev" — phase 2 adds a `--judgments`
    # provenance read to score.py, which must not count as invoking the judge).
    import sacredbench.collect as collect
    import sacredbench.score as score
    forbidden = ("jev.judge", "post_decision", "alpha/decisions", "build_questions")
    for mod in (score, collect):
        src = Path(mod.__file__).read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in src, f"{mod.__name__} invokes the judge ({token})"


# ---- `score` CLI: the grader seam + the --judgments provenance opt-in -----

def _score_answers(tmp_path):
    answers = tmp_path / "answers.jsonl"
    answers.write_text(json.dumps({
        "question_id": "retrieve_quote-0", "model_id": "m1", "task": "retrieve_quote",
        "answer": "x", "question_set_digest": "d",
        "question": {"expected": {"text": "x"}, "source": {"tradition": ["A"]}},
    }) + "\n", encoding="utf-8")
    return answers


def test_score_cli_rejects_jev_as_inline_evaluator(tmp_path):
    from typer.testing import CliRunner
    from sacredbench.cli import app

    r = CliRunner().invoke(app, ["score", str(_score_answers(tmp_path)),
                                 "--scores-out", str(tmp_path / "s.jsonl"),
                                 "--summary-out", str(tmp_path / "sum.json"),
                                 "--evaluator", "jev"])
    assert r.exit_code != 0
    assert "separate-pass" in r.output


def test_score_cli_judgments_records_provenance(tmp_path):
    from typer.testing import CliRunner
    from sacredbench.cli import app
    from sacredbench.jev import RUBRIC_ID

    sidecar = tmp_path / "judgments.jsonl"
    sidecar.write_text(json.dumps({
        "question_id": "retrieve_quote-0", "model_id": "m1", "rubric_id": RUBRIC_ID,
        "judge_model": "jev-latest", "judge_model_resolved": "typesafe/jev-1.14-20261014",
        "question_set_digest": "d", "answer_digest": answer_digest("x"),  # binds to _score_answers' answer "x"
        "refusal_p": 0.1, "matches_requested_p": 0.9, "equivalence": "not_evaluated",
    }) + "\n", encoding="utf-8")
    (tmp_path / "judgments.jsonl.manifest.json").write_text(json.dumps({
        "rubric_id": RUBRIC_ID, "judge_model": "jev-latest",
        "judge_model_resolved": "typesafe/jev-1.14-20261014",
        "question_set_digest": "d", "index_digest": None,
    }), encoding="utf-8")

    summary_out = tmp_path / "sum.json"
    r = CliRunner().invoke(app, ["score", str(_score_answers(tmp_path)),
                                 "--scores-out", str(tmp_path / "s.jsonl"),
                                 "--summary-out", str(summary_out),
                                 "--judgments", str(sidecar)])
    assert r.exit_code == 0, r.output
    summary = json.loads(summary_out.read_text(encoding="utf-8"))
    assert summary["judge"] == {"model_resolved": "typesafe/jev-1.14-20261014", "rubric_id": RUBRIC_ID}
    assert isinstance(summary["evaluators"], list)
    assert "cost" not in json.dumps(summary).lower()


# ---- equivalence index consumer (Spec 21 phase 3, #32 schema verbatim) ----

def _write_index(tmp_path, *, name="eqindex", corpus_hash=INDEX_CORPUS_HASH, rows=None,
                 row_count=None, digest=None):
    """A minimal #32-schema index + manifest under tmp_path; returns the index file path. The manifest
    digest is the REAL sha256[:16] of the written bytes (matching the producer) unless overridden;
    row_count defaults to len(rows). Pass `digest=`/`row_count=` to force a mismatch for a negative test."""
    if rows is None:
        rows = [{"work": "The Bible", "citation": "Isaiah 1:1", "language": "en",
                 "wordings": [{"version": "KJV", "text": "the requested line of scripture here"},
                              {"version": "ASV", "text": "an alternate indexed wording"}]}]
    idx = tmp_path / f"{name}.jsonl"
    body = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    idx.write_text(body, encoding="utf-8")
    real = hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]
    (tmp_path / f"{name}.jsonl.manifest.json").write_text(json.dumps({
        "corpus_hash": corpus_hash,
        "row_count": len(rows) if row_count is None else row_count,
        "digest": real if digest is None else digest,
        "excluded_restricted": [],
    }), encoding="utf-8")
    return idx


def test_load_equivalence_index_happy_path_from_committed_fixture():
    idx = load_equivalence_index(INDEX_FIXTURE, run_corpus_hash=INDEX_CORPUS_HASH)
    assert isinstance(idx, EquivalenceIndex)
    assert idx.corpus_hash == INDEX_CORPUS_HASH and idx.digest == "193ba2f4ebe1ddb6"
    assert idx.row_count == 2
    # .wordings excludes the requested edition (by version) and returns the OTHER indexed wording(s)
    others = idx.wordings("The Bible", "Isaiah 1:1", "en", "KJV", "the requested line of scripture here")
    assert [w["version"] for w in others] == ["ASV"]
    # a citation absent from the index → no alternates (never a silent no-match upstream)
    assert idx.wordings("The Bible", "Nahum 1:1", "en", "KJV", "x") == []


def test_wordings_excludes_by_version_not_exact_text(tmp_path):
    # orthographic drift: the index's KJV text differs from question.expected.text by punctuation,
    # but it is still the REQUESTED edition and must not leak into indexed_other_wordings (else a
    # false other_indexed_wording verdict). Exclusion is by version, so it is dropped regardless.
    rows = [{"work": "The Bible", "citation": "Isaiah 1:1", "language": "en", "wordings": [
        {"version": "KJV", "text": "the requested line of scripture here."},   # trailing period drift
        {"version": "ASV", "text": "an alternate wording"}]}]
    idx = load_equivalence_index(_write_index(tmp_path, rows=rows, row_count=1),
                                 run_corpus_hash=INDEX_CORPUS_HASH)
    others = idx.wordings("The Bible", "Isaiah 1:1", "en", "KJV", "the requested line of scripture here")
    assert [w["version"] for w in others] == ["ASV"]  # KJV dropped by VERSION despite the text drift


def test_load_equivalence_index_restricted_wording_fails_fast(tmp_path):
    # baked constraint: an index wording for a RESTRICTED target must never reach the judge
    rows = [{"work": "NABRE Bible", "citation": "Gen 1:1", "language": "en", "wordings": [
        {"version": "NABRE", "text": "secret restricted text"},
        {"version": "PUBLIC", "text": "public text"}]}]
    idx = _write_index(tmp_path, rows=rows, row_count=1)
    restricted = frozenset({("NABRE Bible", "NABRE", "en")})
    with pytest.raises(JevError, match="RESTRICTED target"):
        load_equivalence_index(idx, run_corpus_hash=INDEX_CORPUS_HASH, restricted_keys=restricted)


def test_load_equivalence_index_corpus_hash_mismatch_fails_fast():
    with pytest.raises(JevError, match="differs from the run's"):
        load_equivalence_index(INDEX_FIXTURE, run_corpus_hash="some-other-corpus")


def test_load_equivalence_index_missing_manifest_fails_fast(tmp_path):
    idx = tmp_path / "bare.jsonl"
    idx.write_text('{"work":"W","citation":"1:1","language":"en","wordings":[{"version":"a","text":"x"}]}\n')
    with pytest.raises(JevError, match="no equivalence-index manifest"):
        load_equivalence_index(idx, run_corpus_hash=INDEX_CORPUS_HASH)


def test_load_equivalence_index_row_count_disagrees_fails_fast(tmp_path):
    idx = _write_index(tmp_path, row_count=5)  # manifest claims 5, file has 1
    with pytest.raises(JevError, match="row_count"):
        load_equivalence_index(idx, run_corpus_hash=INDEX_CORPUS_HASH)


def test_load_equivalence_index_malformed_wording_fails_fast(tmp_path):
    bad = [{"work": "W", "citation": "1:1", "language": "en", "wordings": [{"version": "a"}]}]  # no text
    idx = _write_index(tmp_path, row_count=1, rows=bad)
    with pytest.raises(JevError, match="wording missing"):
        load_equivalence_index(idx, run_corpus_hash=INDEX_CORPUS_HASH)


def test_judge_with_index_asks_equivalence_and_records_index_digest(tmp_path):
    idx = load_equivalence_index(INDEX_FIXTURE, run_corpus_hash=INDEX_CORPUS_HASH)
    out = tmp_path / "j.jsonl"
    seen = {}

    def decide(state):
        seen["state"] = state  # capture what the judge sent
        return _payload(kind="other_indexed_wording")

    # no explicit index_digest — judge derives it from index.digest (the digest is the index's identity)
    done, failed, _ = judge([_row(qsd="d")], out, index=idx, decide=decide, concurrency=1,
                            question_set_digest="d")
    assert (done, failed) == (1, 0)
    # the equivalence question was asked: the state carried the OTHER indexed wordings
    assert seen["state"]["indexed_other_wordings"] == [{"version": "ASV", "text": "an alternate indexed wording of the same verse"}]
    row = json.loads(out.read_text(encoding="utf-8").strip())
    assert row["kind"] == "other_indexed_wording"
    assert row["index_digest"] == idx.digest
    assert "equivalence" not in row  # evaluated ⇒ flat kind, not the sentinel
    manifest = json.loads((tmp_path / "j.jsonl.manifest.json").read_text(encoding="utf-8"))
    assert manifest["index_digest"] == idx.digest


def test_judge_rejects_index_digest_that_disagrees_with_index(tmp_path):
    # the footgun codex named: an index paired with a contradicting explicit digest is refused
    idx = load_equivalence_index(INDEX_FIXTURE, run_corpus_hash=INDEX_CORPUS_HASH)
    with pytest.raises(JevError, match="differs from the supplied index"):
        judge([_row(qsd="d")], tmp_path / "j.jsonl", index=idx, index_digest="not-the-index-digest",
              decide=lambda s: _payload(kind="neither"), concurrency=1, question_set_digest="d")


def test_judge_index_digest_without_index_fails_fast(tmp_path):
    with pytest.raises(JevError, match="without an index"):
        judge([_row(qsd="d")], tmp_path / "j.jsonl", index_digest="orphan",
              decide=lambda s: _payload(), concurrency=1, question_set_digest="d")


def test_judge_without_index_records_not_evaluated(tmp_path):
    out = tmp_path / "j.jsonl"
    judge([_row(qsd="d")], out, decide=lambda s: _payload(), concurrency=1, question_set_digest="d")
    row = json.loads(out.read_text(encoding="utf-8").strip())
    assert row["equivalence"] == "not_evaluated" and "kind" not in row and "index_digest" not in row


_INDEX_ROWS_B = [{"work": "The Bible", "citation": "Genesis 1:1", "language": "en",
                  "wordings": [{"version": "KJV", "text": "in the beginning"},
                               {"version": "ASV", "text": "in the beginning (asv)"}]}]


def test_judge_mixed_index_resume_fails_fast(tmp_path):
    out = tmp_path / "j.jsonl"
    # two DIFFERENT-content indexes, same corpus_hash → different REAL digests (no digest override)
    idx_a = load_equivalence_index(_write_index(tmp_path, name="a"),
                                   run_corpus_hash=INDEX_CORPUS_HASH)
    idx_b = load_equivalence_index(_write_index(tmp_path, name="b", rows=_INDEX_ROWS_B),
                                   run_corpus_hash=INDEX_CORPUS_HASH)
    assert idx_a.digest != idx_b.digest
    judge([_row(qid="q-A", qsd="d")], out, index=idx_a,
          decide=lambda s: _payload(kind="neither"), concurrency=1, question_set_digest="d")
    # resuming with a DIFFERENT index (same corpus_hash) is refused by the manifest check — no
    # mixed-index sidecar even when corpus_hash is unchanged
    with pytest.raises(JevError, match="index digest"):
        judge([_row(qid="q-B", qsd="d")], out, index=idx_b,
              decide=lambda s: _payload(kind="neither"), concurrency=1, question_set_digest="d")


def test_judge_resume_rejects_row_with_conflicting_index_digest(tmp_path):
    # codex iter-1: the manifest check alone is not enough — a row whose index_digest conflicts with
    # the pinned one must also be refused (no mixed-index rows under a matching manifest).
    out = tmp_path / "j.jsonl"
    idx = load_equivalence_index(_write_index(tmp_path, name="a"),
                                 run_corpus_hash=INDEX_CORPUS_HASH)
    judge([_row(qid="q-A", qsd="d")], out, index=idx,
          decide=lambda s: _payload(kind="neither"), concurrency=1, question_set_digest="d")
    # hand-corrupt a row's index_digest, leaving the manifest intact
    rows = out.read_text(encoding="utf-8").splitlines()
    bad = json.loads(rows[0]); bad["index_digest"] = "idx-OTHER"; bad["question_id"] = "q-Z"
    out.write_text("\n".join(rows + [json.dumps(bad)]) + "\n", encoding="utf-8")
    with pytest.raises(JevError, match="row equivalence-index digest"):
        judge([_row(qid="q-B", qsd="d")], out, index=idx,
              decide=lambda s: _payload(kind="neither"), concurrency=1, question_set_digest="d")


def test_judge_cli_equivalence_index_requires_questions(tmp_path, monkeypatch):
    import sacredbench.cli as climod
    from typer.testing import CliRunner
    from sacredbench.cli import app

    monkeypatch.setattr(climod, "_require_catalogue", lambda root: [])
    answers = tmp_path / "answers.jsonl"
    answers.write_text(json.dumps(_row(qsd="d")) + "\n", encoding="utf-8")
    r = CliRunner().invoke(app, ["judge", str(answers), "--out", str(tmp_path / "j.jsonl"),
                                 "--equivalence-index", str(INDEX_FIXTURE)])
    assert r.exit_code != 0
    # Typer draws the BadParameter in a wrapped box, so the phrase is not one contiguous
    # substring of r.output. Strip the box and collapse whitespace before matching.
    plain = re.sub(r"\x1b\[[0-9;]*m", "", r.output)
    plain = re.sub(r"[\u2500-\u257F]", " ", plain)
    plain = re.sub(r"\s+", " ", plain)
    assert "requires --questions" in plain


def test_judge_cli_corpus_hash_mismatch_fails_fast(tmp_path, monkeypatch):
    import sacredbench.cli as climod
    from typer.testing import CliRunner
    from sacredbench.cli import app

    monkeypatch.setattr(climod, "_require_catalogue", lambda root: [])
    answers = tmp_path / "answers.jsonl"
    answers.write_text(json.dumps(_row(qsd="d")) + "\n", encoding="utf-8")
    questions = tmp_path / "questions.jsonl"
    questions.write_text("", encoding="utf-8")
    (tmp_path / "questions.jsonl.manifest.json").write_text(
        json.dumps({"corpus_hash": "a-different-corpus", "question_set_digest": "d"}), encoding="utf-8")
    r = CliRunner().invoke(app, ["judge", str(answers), "--out", str(tmp_path / "j.jsonl"),
                                 "--equivalence-index", str(INDEX_FIXTURE), "--questions", str(questions)])
    # JevError propagates (CliRunner invokes the app, not main()'s catch) — it's the fail-fast, and
    # main() formats it as `error: …` exit 2 in a real invocation.
    assert r.exit_code != 0
    assert isinstance(r.exception, JevError) and "differs from the run's" in str(r.exception)


def test_judge_cli_mispointed_questions_fails_fast(tmp_path, monkeypatch):
    # claude #3: --questions bound by question_set_digest to THESE answers; a different run's
    # questions file (wrong digest) is refused before its corpus_hash can be used.
    import sacredbench.cli as climod
    from typer.testing import CliRunner
    from sacredbench.cli import app

    monkeypatch.setattr(climod, "_require_catalogue", lambda root: [])
    answers = tmp_path / "answers.jsonl"
    answers.write_text(json.dumps(_row(qsd="d")) + "\n", encoding="utf-8")
    questions = tmp_path / "questions.jsonl"
    questions.write_text("", encoding="utf-8")
    # matching corpus_hash but a DIFFERENT question_set_digest → a different run's questions file
    (tmp_path / "questions.jsonl.manifest.json").write_text(
        json.dumps({"corpus_hash": INDEX_CORPUS_HASH, "question_set_digest": "other-run"}), encoding="utf-8")
    r = CliRunner().invoke(app, ["judge", str(answers), "--out", str(tmp_path / "j.jsonl"),
                                 "--equivalence-index", str(INDEX_FIXTURE), "--questions", str(questions)])
    assert r.exit_code != 0
    # the message's multi-word phrase is box-wrapped by typer; match single unsplittable tokens
    assert "question_set_digest" in r.output and "other-run" in r.output


def _eq_cli(tmp_path, monkeypatch, *, answers_qsd="d", manifest):
    """Invoke `judge --equivalence-index <fixture> --questions <q>` with a given answers digest and a
    given questions-manifest dict; returns the CliRunner result. Catalogue is stubbed (no restricted)."""
    import sacredbench.cli as climod
    from typer.testing import CliRunner
    from sacredbench.cli import app

    monkeypatch.setattr(climod, "_require_catalogue", lambda root: [])
    answers = tmp_path / "answers.jsonl"
    answers.write_text(json.dumps(_row(qsd=answers_qsd)) + "\n", encoding="utf-8")
    questions = tmp_path / "questions.jsonl"
    questions.write_text("", encoding="utf-8")
    (tmp_path / "questions.jsonl.manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return CliRunner().invoke(app, ["judge", str(answers), "--out", str(tmp_path / "j.jsonl"),
                                    "--equivalence-index", str(INDEX_FIXTURE), "--questions", str(questions)])


def test_judge_cli_questions_manifest_without_digest_fails_fast(tmp_path, monkeypatch):
    # codex iter-2: a manifest lacking question_set_digest must NOT be accepted (its corpus_hash would
    # bind the index unverified) when there is an answers digest to bind to.
    r = _eq_cli(tmp_path, monkeypatch, answers_qsd="d", manifest={"corpus_hash": INDEX_CORPUS_HASH})
    assert r.exit_code != 0
    assert "describes" in r.output  # "...cannot confirm --questions describes these answers"


def test_judge_cli_answers_without_digest_fails_fast(tmp_path, monkeypatch):
    # claude #1: answers with no question_set_digest give nothing to bind the index to → refuse,
    # rather than silently skipping the binding and trusting an arbitrary --questions corpus_hash.
    r = _eq_cli(tmp_path, monkeypatch, answers_qsd=None,
                manifest={"corpus_hash": INDEX_CORPUS_HASH, "question_set_digest": "d"})
    assert r.exit_code != 0
    assert "coherent" in r.output  # "...re-collect to a coherent set before judging with an index"


def test_estimate_mixed_index_fails_fast(tmp_path):
    # the CLI runs estimate() BEFORE judge(), so the mixed-index error a user hits first surfaces from
    # estimate — assert that path directly (test_judge_mixed_index_resume_fails_fast covers judge()).
    out = tmp_path / "j.jsonl"
    idx_a = load_equivalence_index(_write_index(tmp_path, name="a"),
                                   run_corpus_hash=INDEX_CORPUS_HASH)
    judge([_row(qid="q-A", qsd="d")], out, index=idx_a,
          decide=lambda s: _payload(kind="neither"), concurrency=1, question_set_digest="d")
    with pytest.raises(JevError, match="index digest"):
        estimate([_row(qid="q-B", qsd="d")], out, index_digest="definitely-not-the-real-digest",
                 question_set_digest="d")


# ---- PR #47 round-1 hardening: digest verify, typed-response validation, required digest ----

def test_load_equivalence_index_tampered_file_same_row_count_fails_fast(tmp_path):
    # edit a wording's text in place (row_count unchanged) without updating the manifest → digest fail
    idx = _write_index(tmp_path)
    body = idx.read_text(encoding="utf-8")
    idx.write_text(body.replace("an alternate indexed wording", "TAMPERED wording"), encoding="utf-8")
    with pytest.raises(JevError, match="was modified without updating its manifest"):
        load_equivalence_index(idx, run_corpus_hash=INDEX_CORPUS_HASH)


def test_interpret_rejects_incomplete_or_out_of_range_choice():
    p = _payload(kind="neither"); del p["answers"]["kind"]["probabilities"]["refusal"]
    with pytest.raises(JevError, match="missing label"):
        interpret(p, with_equivalence=True)
    p = _payload(kind="neither"); p["answers"]["kind"]["probabilities"]["refusal"] = "high"
    with pytest.raises(JevError, match="probabilities"):
        interpret(p, with_equivalence=True)
    p = _payload(kind="neither"); p["answers"]["kind"]["probabilities"]["refusal"] = 1.5
    with pytest.raises(JevError, match="probabilities"):
        interpret(p, with_equivalence=True)
    p = _payload(kind="neither"); p["answers"]["kind"]["confidence"] = 1.5
    with pytest.raises(JevError, match="confidence"):
        interpret(p, with_equivalence=True)


def test_interpret_rejects_negative_usage():
    p = _payload(); p["usage"]["cost"] = -0.01
    with pytest.raises(JevError, match="cost"):
        interpret(p, with_equivalence=False)
    p = _payload(); p["usage"]["input_tokens"] = -1
    with pytest.raises(JevError, match="token counts"):
        interpret(p, with_equivalence=False)


def test_judge_requires_a_question_set_digest(tmp_path):
    with pytest.raises(JevError, match="no question_set_digest"):
        estimate([_row(qid="q1", qsd=None)], tmp_path / "j.jsonl")
