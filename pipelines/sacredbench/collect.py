"""Collection: fan every question out to every configured model.

Discipline ported from the multibench judging workflow:

- **Resumable**: answers append to ``answers.jsonl``; cells already answered
  (question_id, model_id) are skipped on re-run, so a crashed or partial run
  continues instead of re-paying.
- **Concurrency-bounded parallel** over provider calls (``concurrency`` in the
  run config); ``concurrency: 1`` is strictly serial.
- **Failed cells stay pending** and make the run exit non-zero — nothing is
  silently dropped, a re-run retries exactly the missing cells.
"""

from __future__ import annotations

import json
import os
import signal
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from sacredbench.config import RunConfig
from sacredbench.generate import Question, question_set_digest
from sacredbench.providers import complete, is_fatal_error


class CollectError(Exception):
    """Collection cannot proceed (e.g. resuming against a different question set)."""


class Stopped(BaseException):
    """Ctrl+C. Finished answers are already on disk. The caller must os._exit."""


class _DaemonPool(ThreadPoolExecutor):
    """Worker threads are daemons, so Ctrl+C can exit without waiting out the HTTP timeout.

    A thread's daemon flag is inherited from the thread that creates it, so the stock
    ``_adjust_thread_count`` is run from a short-lived daemon thread: the workers it spawns are
    daemons, with no copy of CPython's version-specific worker wiring (#97: 3.14 removed the
    ``_initializer``/``_initargs`` attributes an earlier copy read)."""

    def _adjust_thread_count(self):
        adjust = super()._adjust_thread_count
        failure: list[BaseException] = []

        def spawn():
            try:
                adjust()
            except BaseException as e:  # noqa: BLE001 — re-raised on the submitting thread
                failure.append(e)

        spawner = threading.Thread(target=spawn, daemon=True)
        spawner.start()
        spawner.join()
        if failure:
            raise failure[0]


def _panel_fingerprint(m) -> str:
    """A model cell's panel identity — so a model id can't be silently re-pointed at a
    different provider/model/host/tools between resumes. The tools setting is part of the
    identity (Spec 8): a web-search-on cell must never be resumed as web-search-off.
    Temperature joins the identity only when set, so existing runs' fingerprints are
    unchanged (an unset temperature means the host default stood)."""
    base = f"{m.provider}|{m.model}|{m.base_url or ''}|{','.join(m.tools)}"
    if m.temperature is not None:
        base += f"|t={m.temperature}"
    return base


def _existing(
    answers_path: Path,
) -> tuple[set[tuple[str, str]], set[str], int, dict[str, set[str]], set[str]]:
    """Return ((question_id, model_id) keys, digests present, rows missing a digest,
    {model_id: panel fingerprints seen}, {model_id with >=1 row carrying NO fingerprint}).

    The last set is the evidence-integrity guard: a row with no ``panel_fingerprint``
    (e.g. a pre-Spec-3 answers file — first-run's rows carry a digest but no fingerprint)
    contributes nothing to the identity-mismatch check below, so without tracking it a
    legacy file could be silently resumed/scored under a *different* tools identity."""
    keys: set[tuple[str, str]] = set()
    digests: set[str] = set()
    missing = 0
    fps: dict[str, set[str]] = {}
    fp_missing: set[str] = set()
    if not answers_path.exists():
        return keys, digests, missing, fps, fp_missing
    with open(answers_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                d = json.loads(line)
                keys.add((d["question_id"], d["model_id"]))
                if d.get("question_set_digest"):
                    digests.add(d["question_set_digest"])
                else:
                    missing += 1
                fp = d.get("panel_fingerprint")
                if fp:
                    fps.setdefault(d["model_id"], set()).add(fp)
                else:
                    fp_missing.add(d["model_id"])
    return keys, digests, missing, fps, fp_missing


def carry_forward(
    questions: list[Question],
    config: RunConfig,
    answers_path: Path,
    source: Path,
    digest_from: list[Question] | None = None,
) -> int:
    """Copy answers from an earlier answers file instead of calling the model again (#85).

    A row is carried only when its question id AND prompt text are byte-identical to a question
    here, and its panel fingerprint and max_tokens match the configured model: the model saw exactly
    this prompt under this identity, so its answer stands. The copy is re-stamped with this file's
    digest and question (``score`` reads ``expected`` from it) and records ``carried_from``. Cells
    already in ``answers_path`` are never overwritten. Returns the number of rows carried.
    """
    digest = question_set_digest(digest_from if digest_from is not None else questions)
    done_keys, existing_digests, missing, _, _ = _existing(answers_path)
    if (existing_digests - {digest}) or missing:
        raise CollectError(f"{answers_path} was not built for this question set; refusing to carry into it")
    by_id = {q.id: q for q in questions}
    models = {m.id: m for m in config.models}
    carried = []
    for line in source.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        q, m = by_id.get(row["question_id"]), models.get(row["model_id"])
        if q is None or m is None or (q.id, m.id) in done_keys or row["question"]["prompt"] != q.prompt:
            continue
        if row.get("panel_fingerprint") != _panel_fingerprint(m) or row.get("max_tokens") != m.max_tokens:
            continue
        done_keys.add((q.id, m.id))
        carried.append({
            **row, "question_set_digest": digest, "question": asdict(q),
            "carried_from": {
                "answers": os.path.relpath(source, answers_path.parent),
                "question_set_digest": row.get("question_set_digest"),
            },
        })
    answers_path.parent.mkdir(parents=True, exist_ok=True)
    with open(answers_path, "a", encoding="utf-8") as f:
        for row in carried:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return len(carried)


def collect(
    questions: list[Question],
    config: RunConfig,
    answers_path: Path,
    on_result=None,
    on_failure=None,
    digest_from: list[Question] | None = None,
) -> tuple[int, int, list[str]]:
    """Run all pending (question, model) cells. Returns (done, failed, failure_messages).

    The question-set digest is stamped into every answer row; resuming against an
    ``answers.jsonl`` built for a different question set is refused (``CollectError``)
    so a stale or mixed run can never be silently appended to or scored.

    ``on_result`` is called with the saved answer row. ``on_failure`` is called
    with the question, model, and exception. ``questions`` is what this invocation
    calls. ``digest_from`` is the whole file
    when this invocation is a pilot (one tradition, one model). The stamp stays the
    file's digest, so a later full run can resume the same answers file.
    """
    digest = question_set_digest(digest_from if digest_from is not None else questions)
    done_keys, existing_digests, missing, existing_fps, existing_fp_missing = _existing(answers_path)
    if (existing_digests - {digest}) or missing:
        raise CollectError(
            f"{answers_path} was not built for this question set (current digest {digest}; "
            f"found digest(s) {sorted(existing_digests) or 'none'}, {missing} row(s) with no "
            "digest); refusing to resume — regenerate or point --out at a fresh file"
        )
    # panel-identity binding: a model id already answered under one provider/model must
    # not be resumed under a different one (its old answers would hide under new metadata)
    for m in config.models:
        current = _panel_fingerprint(m)
        # A legacy row with NO fingerprint (first-run shape: digest but no panel_fingerprint)
        # bypasses the mismatch check below, so a partial pre-Spec-3 file could resume under a
        # tools-bearing identity and silently mix web-search-on and -off answers. Refuse it.
        if m.id in existing_fp_missing:
            raise CollectError(
                f"{answers_path}: model id {m.id!r} has answer row(s) with no panel fingerprint "
                "(a pre-Spec-3 answers file); refusing to resume — such rows cannot be identity-"
                "checked and could silently mix web-search-on and -off answers under one id. "
                "Point --out at a fresh file (or re-collect)."
            )
        mismatched = existing_fps.get(m.id, set()) - {current}
        if mismatched:
            raise CollectError(
                f"{answers_path}: model id {m.id!r} has answers from a different panel identity "
                f"{sorted(mismatched)}, but the config now maps it to {current!r}; refusing to "
                "resume under a changed identity — use a fresh --out or a distinct model id"
            )
    cells = [
        (q, m) for q in questions for m in config.models if (q.id, m.id) not in done_keys
    ]
    answers_path.parent.mkdir(parents=True, exist_ok=True)
    write_lock = threading.Lock()
    failures: list[str] = []
    done = 0
    stop = threading.Event()

    def run_cell(q: Question, m) -> None:
        nonlocal done
        if stop.is_set():
            return
        started = datetime.now(timezone.utc)
        t0 = time.perf_counter()
        try:
            text, usage, attempts = complete(m, q.prompt)  # raises on failure
        except Exception as e:
            if is_fatal_error(e):
                stop.set()
            raise
        finished = datetime.now(timezone.utc)
        row = {
            "question_id": q.id,
            "model_id": m.id,
            "model": m.model,
            "provider": m.provider,
            "max_tokens": m.max_tokens,
            "temperature": m.temperature,
            "panel_fingerprint": _panel_fingerprint(m),
            "task": q.task,
            "answer": text,
            "usage": usage,
            "attempts": attempts,
            "question_set_digest": digest,
            "started_at": started.isoformat(),
            "collected_at": finished.isoformat(),
            "duration_s": round(time.perf_counter() - t0, 3),
            "question": asdict(q),
        }
        with write_lock:
            with open(answers_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
            done += 1
            if on_result:
                on_result(row)

    pool = _DaemonPool(max_workers=config.concurrency, thread_name_prefix="sacredbench")
    interrupts = 0
    previous_sigint = signal.getsignal(signal.SIGINT)

    def on_sigint(signum, frame):
        nonlocal interrupts
        interrupts += 1
        stop.set()
        if interrupts >= 2:
            os._exit(130)
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, on_sigint)
    try:
        futures = {pool.submit(run_cell, q, m): (q, m) for q, m in cells}
        for fut in as_completed(futures):
            q, m = futures[fut]
            try:
                fut.result()
            except Exception as e:  # noqa: BLE001 — record any failure, keep the cell pending
                failures.append(f"{q.id} x {m.id}: {e}")
                if on_failure:
                    on_failure(q, m, e)
                if is_fatal_error(e):
                    stop.set()
                    for pending in futures:
                        pending.cancel()
                    break
    except KeyboardInterrupt:
        stop.set()
        raise Stopped("stopped. Finished answers are saved. Run the same command to continue.")
    finally:
        signal.signal(signal.SIGINT, previous_sigint)
        pool.shutdown(wait=False, cancel_futures=True)

    return done, len(failures), failures
