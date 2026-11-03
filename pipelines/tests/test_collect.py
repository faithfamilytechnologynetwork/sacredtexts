"""Collection resume semantics behind a FAKE provider (no SDKs, no network):
a dead-key cell stays pending and the run reports failures; a fixed re-run fills
exactly the missing cells once; and resuming against a different question set is
refused via the bound question-set digest."""

from __future__ import annotations

import json

import pytest

from sacredbench import collect as collect_mod
from sacredbench.collect import CollectError, collect
from sacredbench.config import ModelSpec, RunConfig
from sacredbench.generate import Question
from sacredbench.providers import ProviderError


def _q(qid: str) -> Question:
    return Question(
        id=qid, task="retrieve_quote", prompt=f"prompt for {qid}",
        expected={"text": "x"},
        source={"tradition": ["T"], "work": "W", "version": "V", "language": "en",
                "document_type": "scripture", "citation": "W 1:1"},
    )


def _config(*ids: str) -> RunConfig:
    return RunConfig(
        models=tuple(ModelSpec(id=i, provider="anthropic", model="m-" + i) for i in ids),
        concurrency=1,
    )


def _fake(dead: set[str]):
    def fake(model, prompt, retries=2):
        if model.id in dead:
            raise ProviderError(f"dead key for {model.id}")
        # the real `complete` seam returns usage ALREADY normalized to {in, out}
        # (providers.py); the fake must match that contract, not the provider-native shape
        return (f"ans:{prompt}", {"in": 1, "out": 1}, 1)

    return fake


def _rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def test_dead_cell_stays_pending_then_refilled_once(tmp_path, monkeypatch):
    questions = [_q("retrieve_quote-aaaaaa"), _q("retrieve_quote-bbbbbb")]
    config = _config("good", "dead")
    answers = tmp_path / "answers.jsonl"

    # round 1: the "dead" model fails every cell -> those stay pending, run reports failures
    monkeypatch.setattr(collect_mod, "complete", _fake({"dead"}))
    done, failed, messages = collect(questions, config, answers)
    assert done == 2 and failed == 2 and len(messages) == 2  # 2 good written, 2 dead failed
    rows = _rows(answers)
    assert {(r["question_id"], r["model_id"]) for r in rows} == {
        ("retrieve_quote-aaaaaa", "good"), ("retrieve_quote-bbbbbb", "good"),
    }

    # round 2: dead key fixed -> fills EXACTLY the 2 missing cells, re-runs nothing
    monkeypatch.setattr(collect_mod, "complete", _fake(set()))
    done2, failed2, _ = collect(questions, config, answers)
    assert done2 == 2 and failed2 == 0  # only the 2 previously-failed cells
    rows2 = _rows(answers)
    keys = [(r["question_id"], r["model_id"]) for r in rows2]
    assert len(keys) == 4 and len(set(keys)) == 4  # all four cells, exactly once


def test_resume_against_different_question_set_refused(tmp_path, monkeypatch):
    answers = tmp_path / "answers.jsonl"
    config = _config("good")
    monkeypatch.setattr(collect_mod, "complete", _fake(set()))
    collect([_q("retrieve_quote-aaaaaa")], config, answers)  # stamps digest of set A
    with pytest.raises(CollectError) as e:
        collect([_q("retrieve_quote-zzzzzz")], config, answers)  # set B -> different digest
    assert "refusing to resume" in str(e.value)


def test_resume_under_changed_panel_identity_refused(tmp_path, monkeypatch):
    answers = tmp_path / "answers.jsonl"
    monkeypatch.setattr(collect_mod, "complete", _fake(set()))
    qs = [_q("retrieve_quote-aaaaaa")]
    collect(qs, _config("m"), answers)  # model id "m" -> model "m-m", provider anthropic
    # same id, different model string -> panel identity changed -> refuse resume
    changed = RunConfig(models=(ModelSpec(id="m", provider="anthropic", model="other-model"),), concurrency=1)
    with pytest.raises(CollectError, match="different panel identity"):
        collect(qs, changed, answers)
    # the recorded row carries the fingerprint + provider
    row = _rows(answers)[0]
    # fingerprint is provider|model|base_url|tools (tools empty here -> trailing "|")
    assert row["provider"] == "anthropic" and row["panel_fingerprint"] == "anthropic|m-m||"
    # max_tokens is recorded; an unset temperature is recorded as null and stays out of
    # the fingerprint (so existing runs' fingerprints are unchanged)
    assert row["max_tokens"] == 1024 and row["temperature"] is None


def test_legacy_answers_without_digest_refused(tmp_path, monkeypatch):
    answers = tmp_path / "answers.jsonl"
    answers.write_text(json.dumps({"question_id": "retrieve_quote-aaaaaa", "model_id": "good"}) + "\n")
    monkeypatch.setattr(collect_mod, "complete", _fake(set()))
    with pytest.raises(CollectError):
        collect([_q("retrieve_quote-aaaaaa")], _config("good"), answers)


def test_quota_stops_calls_that_have_not_started(tmp_path, monkeypatch):
    calls = []

    def fake(model, prompt, retries=2):
        calls.append(prompt)
        if len(calls) >= 2:
            raise ProviderError("402 Payment Required: insufficient credits")
        return (f"ans:{prompt}", {"in": 1, "out": 1}, 1)

    monkeypatch.setattr(collect_mod, "complete", fake)
    done, failed, messages = collect(
        [_q("a"), _q("b"), _q("c")], _config("m"), tmp_path / "answers.jsonl",
    )
    assert done == 1
    assert failed == 1
    assert len(calls) == 2
    assert not (tmp_path / "errors.jsonl").exists()
    assert "insufficient credits" in messages[0]


def test_pilot_then_rest_resumes_the_same_file(tmp_path, monkeypatch):
    """A one-question pilot stamps the whole file's digest, so the rest can append."""
    from sacredbench.generate import question_set_digest
    answers = tmp_path / "answers.jsonl"
    monkeypatch.setattr(collect_mod, "complete", _fake(set()))
    whole = [_q("a"), _q("b"), _q("c")]
    collect([whole[0]], _config("m"), answers, digest_from=whole)
    collect(whole, _config("m"), answers, digest_from=whole)
    assert {row["question_id"] for row in _rows(answers)} == {"a", "b", "c"}
    assert {row["question_set_digest"] for row in _rows(answers)} == {question_set_digest(whole)}


def test_digest_stamped_into_rows(tmp_path, monkeypatch):
    from sacredbench.generate import question_set_digest
    answers = tmp_path / "answers.jsonl"
    monkeypatch.setattr(collect_mod, "complete", _fake(set()))
    qs = [_q("retrieve_quote-aaaaaa")]
    collect(qs, _config("good"), answers)
    row = _rows(answers)[0]
    assert row["question_set_digest"] == question_set_digest(qs)


# --- #97: _DaemonPool must not reach into ThreadPoolExecutor's version-specific internals -------

def test_daemon_pool_runs_work_on_daemon_threads():
    """The issue's scenario: on 3.14 the old copy of CPython 3.11's ``_adjust_thread_count``
    raised AttributeError on ``_initializer`` at the first submit. Work must run, and on daemon
    threads (so Ctrl+C never waits out an HTTP timeout)."""
    import threading

    pool = collect_mod._DaemonPool(max_workers=2, thread_name_prefix="t97")
    try:
        futures = [pool.submit(lambda: threading.current_thread().daemon) for _ in range(4)]
        assert [f.result(timeout=5) for f in futures] == [True] * 4
    finally:
        pool.shutdown(wait=True)


def test_daemon_pool_surfaces_a_worker_spawn_failure(monkeypatch):
    """Spawning runs on a helper thread; a failure there must still raise out of submit
    (fail fast) rather than leave a queued cell that no worker will ever run."""
    from concurrent.futures import ThreadPoolExecutor

    def cannot_spawn(self):
        raise RuntimeError("can't start new thread")

    monkeypatch.setattr(ThreadPoolExecutor, "_adjust_thread_count", cannot_spawn)
    pool = collect_mod._DaemonPool(max_workers=1)
    try:
        with pytest.raises(RuntimeError, match="can't start new thread"):
            pool.submit(lambda: None)
    finally:
        pool.shutdown(wait=False, cancel_futures=True)


def test_collect_reads_no_private_threadpool_internals():
    """Version-independent pin (CI runs 3.11, where the old code happened to work): collect.py
    must not import ``concurrent.futures.thread`` or touch the worker wiring CPython 3.14
    removed/re-signed (``_initializer``, ``_initargs``, ``_worker``, ``_threads_queues``)."""
    import ast
    from pathlib import Path

    tree = ast.parse(Path(collect_mod.__file__).read_text(encoding="utf-8"))
    private_imports = [
        n.module for n in ast.walk(tree)
        if isinstance(n, ast.ImportFrom) and n.module == "concurrent.futures.thread"
    ]
    private_attrs = sorted({
        n.attr for n in ast.walk(tree)
        if isinstance(n, ast.Attribute)
        and n.attr in {"_initializer", "_initargs", "_worker", "_threads_queues"}
    })
    assert private_imports == [] and private_attrs == []


# --- #85: carry an unchanged question's answer into a rebuilt question set ----------------------

def _changed(q: Question, **fields) -> Question:
    from dataclasses import replace
    return replace(q, **fields)


def test_carry_forward_copies_only_byte_identical_prompts(tmp_path, monkeypatch):
    """A rebuild changed one expected text (same prompt, same id) and one prompt (new id). The first
    answer is carried and re-stamped; the second, and a cell whose identity changed, are called."""
    from sacredbench.generate import question_set_digest

    old_qs = [_q("a"), _q("b"), _q("c")]
    old = tmp_path / "old" / "answers.jsonl"
    monkeypatch.setattr(collect_mod, "complete", _fake(set()))
    collect(old_qs, _config("m", "n"), old)
    new_qs = [
        _changed(old_qs[0], expected={"text": "fixed"}),      # same id + prompt -> carried
        _changed(old_qs[1], id="b2", prompt="new prompt"),    # new prompt -> called
        _changed(old_qs[2], prompt="same id, edited prompt"),  # id kept, prompt differs -> called
    ]
    new = tmp_path / "new" / "answers.jsonl"
    # model "n" now points at a different slug: its old answers must not be carried
    config = RunConfig(
        models=(ModelSpec(id="m", provider="anthropic", model="m-m"),
                ModelSpec(id="n", provider="anthropic", model="other")),
        concurrency=1,
    )
    assert collect_mod.carry_forward(new_qs, config, new, old) == 1
    carried = _rows(new)[0]
    assert (carried["question_id"], carried["model_id"]) == ("a", "m")
    assert carried["answer"] == "ans:prompt for a"
    assert carried["question"]["expected"] == {"text": "fixed"}  # scored against the new expected
    assert carried["question_set_digest"] == question_set_digest(new_qs)
    assert carried["carried_from"] == {
        "answers": "../old/answers.jsonl", "question_set_digest": question_set_digest(old_qs),
    }

    calls = []
    monkeypatch.setattr(collect_mod, "complete", lambda m, p, retries=2: (calls.append((m.id, p)), ("x", {}, 1))[1])
    done, failed, _ = collect(new_qs, config, new)
    assert (done, failed) == (5, 0) and ("m", "prompt for a") not in calls
    assert len(_rows(new)) == 6


def test_carry_forward_never_overwrites_and_refuses_a_foreign_file(tmp_path, monkeypatch):
    qs = [_q("a")]
    monkeypatch.setattr(collect_mod, "complete", _fake(set()))
    old, new = tmp_path / "old.jsonl", tmp_path / "new.jsonl"
    collect(qs, _config("m"), old)
    collect(qs, _config("m"), new)
    assert collect_mod.carry_forward(qs, _config("m"), new, old) == 0  # the cell is already answered
    assert len(_rows(new)) == 1
    # a different max_tokens could have truncated the old answer: it is called, not carried
    shorter = RunConfig(models=(ModelSpec(id="m", provider="anthropic", model="m-m", max_tokens=64),), concurrency=1)
    assert collect_mod.carry_forward(qs, shorter, tmp_path / "fresh.jsonl", old) == 0
    with pytest.raises(CollectError, match="refusing to carry"):
        collect_mod.carry_forward([_q("z")], _config("m"), new, old)
