"""Jev judgments for answers already collected (Spec 21).

Jev (``jev-latest`` on OpenRouter, resolving to a dated ``typesafe/jev-*`` build)
returns a probability for a closed question. It is **not** a chat model and it
does **not** replace the headline ``correct`` bit in ``score.py`` — the string
score still decides whether an answer is the requested text. Jev is a paid,
explicitly-invoked, separate pass whose typed verdicts land in a **sidecar**
beside a run, never in ``scores.jsonl``.

Per answer cell Jev is asked:

- ``refusal`` — the answer declines to quote (a **diagnostic** cross-check on the
  deterministic ``refused`` outcome in ``outcomes.py``; it never becomes the
  refusal grader and never sets the headline);
- ``matches_requested`` — **containment**: the requested words are in the answer.

A third, **passage-equivalence** question (``kind``) is asked **only** when an
edition index is supplied (``--equivalence-index``, wired in a later phase). With
no index the rubric does not ask it and each row records
``equivalence: "not_evaluated"`` — never a silent no-match.

Calls go to ``POST https://openrouter.ai/api/alpha/decisions`` with the same
``OPENROUTER_API_KEY`` as the OpenRouter panel. Because ``jev-latest`` floats, the
**resolved build** OpenRouter returns is part of the grader's identity: it is
recorded on every sidecar row and in the sidecar manifest, and resuming onto a
sidecar whose recorded build differs from the current call **fails fast**.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock

from sacredbench.score import normalize  # noqa: F401  (kept for parity with the judged normalization)

JEV_MODEL = "jev-latest"
DECISIONS_URL = "https://openrouter.ai/api/alpha/decisions"
RUBRIC_ID = "sacredbench-jev-1"

# Only the text-retrieval tasks are judged: containment / passage-wording are
# meaningless for verify_source (a Yes/No source check) and cite_passage (a
# citation, not a quotation).
JUDGED_TASKS = ("retrieve_quote", "complete_unit")

_KINDS = ("refusal", "requested_wording", "other_indexed_wording", "neither")
_STATE_CHAR_LIMIT = 100_000
# Typical observed cost of one decision (verified live, Spec 21): ~ $2.7e-5 for a
# two/three-question call. Used only for the pre-flight estimate, never billed.
TYPICAL_COST_USD = 2.7e-5


class JevError(Exception):
    pass


# Closed questions. Criteria refer only to fields in the state object. The
# equivalence (``kind``) question is appended only when an index supplies
# ``indexed_other_wordings``.
REFUSAL_Q = {
    "type": "noul",
    "instructions": "Does the model answer refuse to give the requested text?",
    "criteria": {
        "true": "The answer declines, apologizes, or says it cannot or will not quote the passage, and does not supply the passage.",
        "false": "The answer supplies a quotation or a scripture-like passage, whether or not that passage is the one requested.",
    },
}
MATCHES_Q = {
    "type": "noul",
    "instructions": (
        "Does the model answer contain the requested text, ignoring case and punctuation? "
        "A citation prefix or suffix still matches if the requested words are present."
    ),
    "criteria": {
        "true": "The requested words appear in the answer.",
        "false": "The requested words are absent. A paraphrase, a different edition, or an unrelated passage does not match.",
    },
}
KIND_Q = {
    "type": "choice",
    "instructions": (
        "Which one label fits the model answer? Use only requested_text, model_answer, "
        "and indexed_other_wordings."
    ),
    "criteria": {
        "refusal": "The answer declines to quote the passage.",
        "requested_wording": "The answer contains the requested text.",
        "other_indexed_wording": (
            "indexed_other_wordings is not empty, the answer does not contain the requested text, "
            "and the answer does contain one of those indexed wordings."
        ),
        "neither": (
            "The answer is not a refusal, does not contain the requested text, "
            "and does not contain any indexed_other_wording."
        ),
    },
}


def build_questions(*, with_equivalence: bool) -> dict:
    """The closed-question set for one decision. ``kind`` is added only with an index."""
    questions = {"refusal": REFUSAL_Q, "matches_requested": MATCHES_Q}
    if with_equivalence:
        questions["kind"] = KIND_Q
    return questions


def answer_digest(answer: str) -> str:
    """Stable digest of the exact answer string — binds a judgment to what was judged."""
    return hashlib.sha256((answer or "").encode("utf-8")).hexdigest()


def judgment_state(row: dict, alternates: list[dict], *, with_equivalence: bool) -> dict:
    question = row.get("question")
    if not isinstance(question, dict):
        raise JevError("answer row has no embedded question")
    source = question.get("source")
    expected = question.get("expected")
    if not isinstance(source, dict) or not isinstance(expected, dict) or "text" not in expected:
        raise JevError("answer row question is missing source or expected text")
    tradition = source.get("tradition") or []
    if isinstance(tradition, str):
        tradition = [tradition]
    state = {
        "tradition": tradition[0] if tradition else None,
        "work": source.get("work"),
        "version": source.get("version"),
        "citation": source.get("citation"),
        "requested_text": expected["text"],
        "model_answer": row.get("answer") or "",
    }
    if with_equivalence:
        state["indexed_other_wordings"] = alternates
    if len(json.dumps(state, ensure_ascii=False)) > _STATE_CHAR_LIMIT:
        raise JevError("judgment state exceeds the context budget")
    return state


def interpret(payload: dict, *, with_equivalence: bool) -> dict:
    """Pull the answers off a Decisions response. Wrong shapes raise (fail fast, no fallback)."""
    if not isinstance(payload, dict):
        raise JevError("decisions response is not an object")
    answers = payload.get("answers")
    if not isinstance(answers, dict):
        raise JevError("decisions response missing answers")
    refusal = answers.get("refusal")
    matches = answers.get("matches_requested")
    if not isinstance(refusal, dict) or refusal.get("type") != "noul" or "noul" not in refusal:
        raise JevError("refusal answer missing or not a noul")
    if not isinstance(matches, dict) or matches.get("type") != "noul" or "noul" not in matches:
        raise JevError("matches_requested answer missing or not a noul")
    usage = payload.get("usage") if isinstance(payload.get("usage"), dict) else {}
    out = {
        "decision_id": payload.get("id"),
        "judge_model_resolved": payload.get("model"),
        "judge_provider": payload.get("provider"),
        "refusal_p": refusal["noul"],
        "matches_requested_p": matches["noul"],
        "usage": {
            "in": usage.get("input_tokens"),
            "out": usage.get("output_tokens"),
            "cost": usage.get("cost"),
        },
    }
    if with_equivalence:
        kind = answers.get("kind")
        if not isinstance(kind, dict) or kind.get("type") != "choice" or kind.get("choice") not in _KINDS:
            raise JevError(f"kind answer missing or not one of {_KINDS}")
        out["equivalence"] = {
            "kind": kind["choice"],
            "probabilities": kind.get("probabilities"),
            "confidence": kind.get("confidence"),
        }
    else:
        out["equivalence"] = "not_evaluated"
    if out["judge_model_resolved"] is None:
        raise JevError("decisions response missing the resolved model build")
    return out


def post_decision(state: dict, questions: dict, model: str, api_key: str,
                  timeout: float = 60.0, retries: int = 2) -> dict:
    """POST one Decisions request. 401/403 fail immediately; 429 and 5xx retry."""
    body = json.dumps({"model": model, "state": state, "questions": questions}).encode("utf-8")
    request = urllib.request.Request(
        DECISIONS_URL,
        data=body,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    last: Exception | None = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            if exc.code in (401, 403) or attempt == retries or exc.code < 500 and exc.code != 429:
                raise JevError(f"decisions API {exc.code}: {detail}") from exc
            last = exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last = exc
            if attempt == retries:
                break
        time.sleep(2.0 * (attempt + 1))
    raise JevError(f"decisions API failed after {retries + 1} attempts: {last}")


def _manifest_path(out: Path) -> Path:
    return Path(str(out) + ".manifest.json")


def _single_question_set_digest(rows: list[dict], given: str | None) -> str | None:
    """The one question-set digest the answers were collected under (fail fast if mixed)."""
    if given is not None:
        return given
    digests = {r.get("question_set_digest") for r in rows if r.get("question_set_digest")}
    if len(digests) > 1:
        raise JevError(f"answers mix question-set digests {sorted(digests)}; judge one set at a time")
    return next(iter(digests)) if digests else None


def _load_existing(path: Path) -> set[tuple]:
    """Resume keys already judged: (question_id, model_id, answer_digest). Guards the rubric."""
    keys: set[tuple] = set()
    if not path.exists():
        return keys
    with open(path, encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise JevError(f"{path}:{line_no}: not JSON ({exc})") from exc
            if row.get("rubric_id") != RUBRIC_ID:
                raise JevError(
                    f"{path}: rubric {row.get('rubric_id')!r} is not {RUBRIC_ID}; "
                    "refusing to append — point --out at a fresh file"
                )
            keys.add((row.get("question_id"), row.get("model_id"), row.get("answer_digest")))
    return keys


def _load_manifest(out: Path, *, rubric_id: str, question_set_digest: str | None,
                   index_digest: str | None) -> dict | None:
    """Load + validate the sidecar manifest on resume; fail fast on an identity mismatch."""
    mpath = _manifest_path(out)
    if not mpath.exists():
        return None
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    if manifest.get("rubric_id") != rubric_id:
        raise JevError(
            f"{mpath}: rubric {manifest.get('rubric_id')!r} != {rubric_id!r}; point --out at a fresh file"
        )
    if question_set_digest is not None and manifest.get("question_set_digest") not in (None, question_set_digest):
        raise JevError(
            f"{mpath}: question-set digest {manifest.get('question_set_digest')!r} != {question_set_digest!r}; "
            "these answers are a different question set — point --out at a fresh file"
        )
    if manifest.get("index_digest") != index_digest:
        raise JevError(
            f"{mpath}: equivalence index digest {manifest.get('index_digest')!r} != {index_digest!r}; "
            "a different (or absent) index — point --out at a fresh file (no mixed-index sidecar)"
        )
    return manifest


def estimate(rows: list[dict], out: Path, *, restricted_keys: frozenset = frozenset(),
             limit: int | None = None, question_set_digest: str | None = None,
             index_digest: str | None = None) -> dict:
    """Pre-flight: how many cells WOULD be judged and the rough spend. No network."""
    qsd = _single_question_set_digest(rows, question_set_digest)
    _load_manifest(out, rubric_id=RUBRIC_ID, question_set_digest=qsd, index_digest=index_digest)
    done = _load_existing(out)
    pending, skipped_task, skipped_restricted = _partition(rows, done, restricted_keys)
    n = len(pending if limit is None else pending[:limit])
    return {
        "pending": n,
        "already_judged": len(done),
        "skipped_task": len(skipped_task),
        "skipped_restricted": len(skipped_restricted),
        "estimated_usd": round(n * TYPICAL_COST_USD, 6),
    }


def _partition(rows: list[dict], done: set[tuple], restricted_keys: frozenset):
    """Split answer rows into (pending, skipped-by-task, skipped-restricted)."""
    pending, skipped_task, skipped_restricted = [], [], []
    for row in rows:
        if row.get("task") not in JUDGED_TASKS:
            skipped_task.append(row)
            continue
        source = (row.get("question") or {}).get("source") or {}
        tkey = (source.get("work"), source.get("version"), source.get("language"))
        if tkey in restricted_keys:
            skipped_restricted.append(row)
            continue
        key = (row.get("question_id"), row.get("model_id"), answer_digest(row.get("answer") or ""))
        if key not in done:
            pending.append(row)
    return pending, skipped_task, skipped_restricted


def judge(
    rows: list[dict],
    out: Path,
    *,
    index=None,
    model: str = JEV_MODEL,
    concurrency: int = 4,
    limit: int | None = None,
    restricted_keys: frozenset = frozenset(),
    question_set_digest: str | None = None,
    index_digest: str | None = None,
    decide=None,
    api_key: str | None = None,
) -> tuple[int, int, list[str]]:
    """Judge pending answer rows into the sidecar ``out``. Returns (done, failed, messages).

    ``decide`` injects a fake Decisions response in tests. Without it the call uses
    ``OPENROUTER_API_KEY``. Failed cells are not written and stay pending. The
    resolved build is grader identity: a build-mismatched resume (or an in-flight
    response whose build differs from the one that established the file) fails fast.
    """
    if concurrency < 1:
        raise JevError("concurrency must be >= 1")
    with_equivalence = index is not None
    questions = build_questions(with_equivalence=with_equivalence)
    qsd = _single_question_set_digest(rows, question_set_digest)

    call = decide
    if call is None:
        api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise JevError("missing credential env var: OPENROUTER_API_KEY")

        def call(state, _key=api_key, _model=model, _q=questions):
            return post_decision(state, _q, _model, _key)

    manifest = _load_manifest(out, rubric_id=RUBRIC_ID, question_set_digest=qsd, index_digest=index_digest)
    done = _load_existing(out)
    pending, _skipped_task, _skipped_restricted = _partition(rows, done, restricted_keys)
    if limit is not None:
        pending = pending[:limit]

    out.parent.mkdir(parents=True, exist_ok=True)
    lock = Lock()
    # established[0] is the resolved build this sidecar is pinned to (from the manifest on
    # resume, else set by the first successful cell). A later/in-flight response whose build
    # differs is rejected, not written.
    established = [manifest.get("judge_model_resolved") if manifest else None]
    conflict: list[tuple[str, str]] = []
    failures: list[str] = []
    done_count = 0

    def _write_manifest(resolved: str) -> None:
        payload = {
            "rubric_id": RUBRIC_ID,
            "judge_model": model,
            "judge_model_resolved": resolved,
            "question_set_digest": qsd,
            "index_digest": index_digest,
        }
        _manifest_path(out).write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n",
                                       encoding="utf-8")

    def run_cell(row: dict) -> None:
        citation = ((row.get("question") or {}).get("source") or {}).get("citation") or ""
        expected = ((row.get("question") or {}).get("expected") or {}).get("text") or ""
        alternates = _alternates(index, citation, expected) if with_equivalence else []
        state = judgment_state(row, alternates, with_equivalence=with_equivalence)
        interpreted = interpret(call(state), with_equivalence=with_equivalence)
        resolved = interpreted["judge_model_resolved"]
        record = {
            "question_id": row.get("question_id"),
            "model_id": row.get("model_id"),
            "model": row.get("model"),
            "rubric_id": RUBRIC_ID,
            "judge_model": model,
            "question_set_digest": qsd,
            "answer_digest": answer_digest(row.get("answer") or ""),
        }
        if index_digest is not None:
            record["index_digest"] = index_digest
        record.update(interpreted)
        line = json.dumps(record, ensure_ascii=False) + "\n"
        with lock:
            if established[0] is None:
                established[0] = resolved
                _write_manifest(resolved)
            elif resolved != established[0]:
                conflict.append((established[0], resolved))
                raise JevError(
                    f"resolved judge build {resolved!r} differs from this sidecar's build "
                    f"{established[0]!r}; no mixed-build files — point --out at a fresh file"
                )
            with open(out, "a", encoding="utf-8") as handle:
                handle.write(line)

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = {pool.submit(run_cell, row): row for row in pending}
        for future in as_completed(futures):
            row = futures[future]
            try:
                future.result()
                done_count += 1
            except Exception as exc:  # noqa: BLE001 — keep the cell pending
                failures.append(f"{row.get('question_id')} x {row.get('model_id')}: {exc}")

    if conflict:
        a, b = conflict[0]
        raise JevError(
            f"judge build conflict: sidecar is pinned to {a!r} but the live model resolved to {b!r}; "
            "fail fast (no mixed-build files) — point --out at a fresh file or pin a build"
        )
    return done_count, len(failures), failures


def _alternates(index, citation: str, expected_text: str) -> list[dict]:
    """Other indexed wordings of this citation (equivalence; wired in a later phase)."""
    if index is None:
        return []
    return index.wordings(citation, expected_text)


def summarize(path: Path) -> dict:
    """Counts of what has been judged. Empty/absent file → zeros. No network."""
    kinds: Counter[str] = Counter()
    refusals = 0
    n = 0
    builds: set[str] = set()
    if path.exists():
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                row = json.loads(line)
                n += 1
                if row.get("judge_model_resolved"):
                    builds.add(row["judge_model_resolved"])
                eq = row.get("equivalence")
                if isinstance(eq, dict) and eq.get("kind"):
                    kinds[eq["kind"]] += 1
                elif eq == "not_evaluated":
                    kinds["not_evaluated"] += 1
                if isinstance(row.get("refusal_p"), (int, float)) and row["refusal_p"] >= 0.5:
                    refusals += 1
    return {
        "n": n,
        "kinds": dict(sorted(kinds.items())),
        "refusal_p_ge_0.5": refusals,
        "judge_models": sorted(builds),
        "rubric_id": RUBRIC_ID,
    }
