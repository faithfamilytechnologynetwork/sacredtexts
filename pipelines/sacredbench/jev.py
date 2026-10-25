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
edition index is supplied (``--equivalence-index``, consuming #32's schema via
``load_equivalence_index``). With no index the rubric does not ask it and each row
records ``equivalence: "not_evaluated"`` — never a silent no-match.

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


def _num(x) -> bool:
    """A real number, not a bool (``True``/``False`` are ints in Python)."""
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _prob(x, field: str) -> float:
    if not _num(x) or not (0.0 <= float(x) <= 1.0):
        raise JevError(f"{field} is not a probability in [0,1]: {x!r}")
    return float(x)


def _nonempty_str(x, field: str) -> str:
    if not isinstance(x, str) or not x:
        raise JevError(f"decisions response missing {field}")
    return x


def interpret(payload: dict, *, with_equivalence: bool) -> dict:
    """Pull the answers off a Decisions response. Wrong shapes/types raise (fail fast, no fallback).

    Every authoritative field is validated: a mistyped probability, a missing decision id /
    provider / resolved build, or a non-numeric cost raises rather than being written — a silently
    tolerated ``cost: None`` would read as zero spend and defeat the budget control.
    """
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
    usage = payload.get("usage")
    if not isinstance(usage, dict):
        raise JevError("decisions response missing usage")
    cost, tin, tout = usage.get("cost"), usage.get("input_tokens"), usage.get("output_tokens")
    if not _num(cost):
        raise JevError(f"decisions usage.cost is not numeric: {cost!r}")
    if not _num(tin) or not _num(tout):
        raise JevError(f"decisions usage token counts are not numeric: in={tin!r} out={tout!r}")
    out = {
        "decision_id": _nonempty_str(payload.get("id"), "the decision id"),
        "judge_model_resolved": _nonempty_str(payload.get("model"), "the resolved model build"),
        "judge_provider": _nonempty_str(payload.get("provider"), "the provider"),
        "refusal_p": _prob(refusal["noul"], "refusal.noul"),
        "matches_requested_p": _prob(matches["noul"], "matches_requested.noul"),
        "usage": {"in": int(tin), "out": int(tout), "cost": float(cost)},
    }
    if with_equivalence:
        kind = answers.get("kind")
        if not isinstance(kind, dict) or kind.get("type") != "choice" or kind.get("choice") not in _KINDS:
            raise JevError(f"kind answer missing or not one of {_KINDS}")
        probs = kind.get("probabilities")
        if not isinstance(probs, dict):
            raise JevError("kind.probabilities missing or not an object")
        conf = kind.get("confidence")
        if not _num(conf):
            raise JevError(f"kind.confidence is not numeric: {conf!r}")
        # Flat fields, matching the spec's authoritative sidecar schema.
        out["kind"] = kind["choice"]
        out["kind_probabilities"] = probs
        out["kind_confidence"] = float(conf)
    else:
        out["equivalence"] = "not_evaluated"
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


def _require_manifest_if_rows(out: Path) -> None:
    """A sidecar with rows but no manifest has no pinned build identity — appending to it could
    silently create a mixed-build file. Refuse."""
    if out.exists() and out.stat().st_size > 0 and not _manifest_path(out).exists():
        raise JevError(
            f"{out} has rows but no manifest ({_manifest_path(out)}); its judge-build identity is "
            "unknown and appending risks a mixed-build file — point --out at a fresh file"
        )


def _single_question_set_digest(rows: list[dict], given: str | None) -> str | None:
    """The one question-set digest the answers were collected under (fail fast if mixed)."""
    if given is not None:
        return given
    digests = {r.get("question_set_digest") for r in rows if r.get("question_set_digest")}
    if len(digests) > 1:
        raise JevError(f"answers mix question-set digests {sorted(digests)}; judge one set at a time")
    if digests and any(not r.get("question_set_digest") for r in rows):
        raise JevError(
            "answers mix rows with and without a question_set_digest; they are not one coherent "
            "question set — regenerate/collect, or judge a single set at a time"
        )
    return next(iter(digests)) if digests else None


def _validate_verdict_row(row: dict, path: Path, line_no: int) -> None:
    """A sidecar row must carry a real typed verdict, not just an identity header. Guards the
    ``load_provenance`` path (``require_verdict``): a *skeletal* row that matches only rubric / build /
    question-set digest would otherwise key as present and let ``score --judgments`` stamp a judge
    build for a sidecar with no actual judgment. Require the resume identity AND the verdict fields:
    ``question_id`` / ``model_id`` / ``answer_digest``, numeric ``refusal_p`` / ``matches_requested_p``
    in [0,1], and either a ``kind`` label or the ``equivalence: "not_evaluated"`` sentinel."""
    for field in ("question_id", "model_id", "answer_digest"):
        if not row.get(field):
            raise JevError(f"{path}:{line_no}: row missing {field}; not a complete judgment")
    _prob(row.get("refusal_p"), f"{path}:{line_no}: refusal_p")
    _prob(row.get("matches_requested_p"), f"{path}:{line_no}: matches_requested_p")
    if not row.get("kind") and row.get("equivalence") != "not_evaluated":
        raise JevError(
            f"{path}:{line_no}: row has neither a `kind` verdict nor `equivalence: not_evaluated`; "
            "not a complete judgment"
        )


_UNCHECKED = object()  # sentinel: "do not check this row field" (vs the legitimate value None)


def _load_existing(path: Path, *, pinned_build: str | None = None,
                   pinned_qsd: str | None = None, require_verdict: bool = False,
                   pinned_index_digest=_UNCHECKED) -> set[tuple]:
    """Resume keys already judged: (question_id, model_id, answer_digest). Guards the rubric and,
    given the manifest's ``pinned_build`` / ``pinned_qsd``, every existing row's resolved build AND
    question-set digest — so a hand-edited or half-written file whose rows disagree with the pinned
    identity is refused, not silently extended. The resume key omits the question-set digest, so a
    row carrying a *different* one (but the same question/model/answer) would otherwise be mistaken
    for a completed cell of the current set; the row-level check closes that (no mixed-set resume,
    no mixed-build files).

    ``require_verdict`` (the ``load_provenance`` path) additionally demands each row carry a complete
    typed verdict (``_validate_verdict_row``), so a skeletal identity-only row cannot pass as a
    judgment. The resume path leaves it ``False`` — its own writes are always complete.

    ``pinned_index_digest`` (the resume path) additionally binds each row's ``index_digest`` to the
    sidecar's pinned equivalence-index identity — so a manifest can't match while a row carries a
    missing or conflicting index digest (a mixed-index sidecar the manifest check alone would miss).
    ``None`` is a real pinned value (a no-index sidecar: rows carry no ``index_digest``); the
    ``_UNCHECKED`` sentinel (the default, used by ``load_provenance``) skips the check entirely."""
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
            row_build = row.get("judge_model_resolved")
            if not row_build:
                raise JevError(
                    f"{path}:{line_no}: row has no judge_model_resolved; its build identity is "
                    "unknown — point --out at a fresh file (no mixed-build files)"
                )
            if pinned_build is not None and row_build != pinned_build:
                raise JevError(
                    f"{path}:{line_no}: row build {row_build!r} differs from the sidecar's pinned "
                    f"build {pinned_build!r}; no mixed-build files — point --out at a fresh file"
                )
            if row.get("question_set_digest") != pinned_qsd:
                raise JevError(
                    f"{path}:{line_no}: row question-set digest {row.get('question_set_digest')!r} "
                    f"differs from the sidecar's {pinned_qsd!r}; these answers are a different "
                    "question set — point --out at a fresh file"
                )
            if pinned_index_digest is not _UNCHECKED and row.get("index_digest") != pinned_index_digest:
                raise JevError(
                    f"{path}:{line_no}: row equivalence-index digest {row.get('index_digest')!r} "
                    f"differs from the sidecar's {pinned_index_digest!r}; no mixed-index files — "
                    "point --out at a fresh file"
                )
            if require_verdict:
                _validate_verdict_row(row, path, line_no)
            keys.add((row.get("question_id"), row.get("model_id"), row.get("answer_digest")))
    return keys


def _load_manifest(out: Path, *, rubric_id: str, question_set_digest: str | None,
                   index_digest: str | None) -> dict | None:
    """Load + validate the sidecar manifest on resume; fail fast on an identity mismatch.

    Parallels ``load_provenance``'s manifest checks deliberately: this resume-path validator binds
    ``index_digest`` (a mixed-index guard), which provenance must NOT constrain once Phase 3 lands —
    keep the two in sync when either manifest field set changes."""
    mpath = _manifest_path(out)
    if not mpath.exists():
        return None
    try:
        manifest = json.loads(mpath.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise JevError(f"{mpath}: not JSON ({exc})") from exc
    if manifest.get("rubric_id") != rubric_id:
        raise JevError(
            f"{mpath}: rubric {manifest.get('rubric_id')!r} != {rubric_id!r}; point --out at a fresh file"
        )
    if not manifest.get("judge_model_resolved"):
        raise JevError(
            f"{mpath}: manifest has no judge_model_resolved; the sidecar's build identity is "
            "unknown and the next response would re-pin it — point --out at a fresh file"
        )
    if manifest.get("question_set_digest") != question_set_digest:
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


def _check_limit(limit: int | None) -> None:
    """A negative cap would slice `pending[:limit]` to all-but-|limit| cells — the opposite of a
    budget guard. Reject it up front (0 means judge nothing, which is allowed)."""
    if limit is not None and limit < 0:
        raise JevError(f"--limit must be >= 0 (got {limit}); it caps cells judged, never uncaps them")


def estimate(rows: list[dict], out: Path, *, restricted_keys: frozenset = frozenset(),
             limit: int | None = None, question_set_digest: str | None = None,
             index_digest: str | None = None) -> dict:
    """Pre-flight: how many cells WOULD be judged and the rough spend. No network."""
    _check_limit(limit)
    qsd = _single_question_set_digest(rows, question_set_digest)
    _require_manifest_if_rows(out)
    manifest = _load_manifest(out, rubric_id=RUBRIC_ID, question_set_digest=qsd, index_digest=index_digest)
    done = _load_existing(out, pinned_build=manifest.get("judge_model_resolved") if manifest else None,
                          pinned_qsd=qsd, pinned_index_digest=index_digest)
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
    _check_limit(limit)
    with_equivalence = index is not None
    # The index's own digest is its identity — never a caller-supplied value that could disagree with
    # the loaded index (which would pin the manifest to one digest while sending another index's
    # wordings). Derive it; reject a mismatched explicit digest; and an index_digest without an index
    # is incoherent (equivalence is off, so there is nothing to pin).
    if index is not None:
        if index_digest is not None and index_digest != index.digest:
            raise JevError(
                f"index_digest {index_digest!r} differs from the supplied index's {index.digest!r}; "
                "do not pass a digest that disagrees with the index"
            )
        index_digest = index.digest
    elif index_digest is not None:
        raise JevError("index_digest supplied without an index; equivalence is off without an index")
    questions = build_questions(with_equivalence=with_equivalence)
    qsd = _single_question_set_digest(rows, question_set_digest)

    call = decide
    if call is None:
        api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise JevError("missing credential env var: OPENROUTER_API_KEY")

        def call(state, _key=api_key, _model=model, _q=questions):
            return post_decision(state, _q, _model, _key)

    _require_manifest_if_rows(out)
    manifest = _load_manifest(out, rubric_id=RUBRIC_ID, question_set_digest=qsd, index_digest=index_digest)
    done = _load_existing(out, pinned_build=manifest.get("judge_model_resolved") if manifest else None,
                          pinned_qsd=qsd, pinned_index_digest=index_digest)
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
        source = (row.get("question") or {}).get("source") or {}
        citation = source.get("citation") or ""
        work = source.get("work")
        language = source.get("language")
        version = source.get("version")
        expected = ((row.get("question") or {}).get("expected") or {}).get("text") or ""
        alternates = _alternates(index, work, citation, language, version, expected) if with_equivalence else []
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


def _alternates(index, work, citation: str, language, requested_version, expected_text: str) -> list[dict]:
    """Other indexed wordings of this ``(work, citation, language)`` (equivalence), excluding the
    question's own edition (``requested_version``). ``[]`` when no index is supplied or the citation
    is absent from it."""
    if index is None:
        return []
    return index.wordings(work, citation, language, requested_version, expected_text)


class EquivalenceIndex:
    """In-memory consumer of #32's equivalence-index file. The schema is **consumed verbatim** (this
    does NOT produce it, and #21 does not depend on #32's branch):

    - index JSONL: one row per ``(work, citation, language)`` —
      ``{work, citation, language, wordings: [{version, text}, …]}`` (single-wording rows omitted by
      the producer; same-canonical-language only; restricted editions already filtered);
    - manifest ``<path>.manifest.json``: ``{corpus_hash, row_count, digest, excluded_restricted}``.

    ``corpus_hash`` binds the index to a run's corpus and ``digest`` is the index identity recorded
    per sidecar row and in the sidecar manifest (so a changed index fails a resume — see
    ``_load_manifest``)."""

    def __init__(self, *, lookup: dict[tuple, list[dict]], corpus_hash: str, digest: str,
                 row_count: int | None):
        self._lookup = lookup
        self.corpus_hash = corpus_hash
        self.digest = digest
        self.row_count = row_count

    def wordings(self, work, citation: str, language, requested_version, expected_text: str) -> list[dict]:
        """The OTHER indexed wordings of this citation: every wording in the row except the requested
        one. The requested wording is identified by **``version``** (the question's own edition), not
        by exact text — an exact-text match is brittle exactly in the Arabic/Hebrew orthographic-variance
        regime this diagnoses (a one-diacritic drift between the index's text and ``expected_text``
        would leave the requested wording in the alternates and invite a false ``other_indexed_wording``
        verdict). A redundant exact-text exclusion is kept as a backstop. ``[]`` when the citation is
        not in the index."""
        rows = self._lookup.get((work, citation, language), [])
        return [w for w in rows
                if w.get("version") != requested_version and w.get("text") != expected_text]


def load_equivalence_index(path: Path, *, run_corpus_hash: str,
                           restricted_keys: frozenset = frozenset()) -> EquivalenceIndex:
    """Load + validate #32's equivalence index, binding it to ``run_corpus_hash``. Fail fast (JevError)
    on a missing manifest, a missing index file, a ``corpus_hash`` mismatch, a malformed row, a
    duplicate ``(work, citation, language)`` key, or a ``row_count`` that disagrees with the file.

    **Restricted-target guard (baked constraint, independent of the commit-time audit gate):** index
    ``wordings[].text`` is sent to the third-party Decisions API, so every wording's
    ``(work, version, language)`` is checked against ``restricted_keys`` here — relying on #32's
    producer to have filtered is exactly the dependence the constraint forbids. A restricted wording
    is a **broken index**, so this fails fast (not a cell-level skip)."""
    mpath = _manifest_path(path)
    if not mpath.exists():
        raise JevError(
            f"{path}: no equivalence-index manifest ({mpath}); #32 writes it beside the index — "
            "point --equivalence-index at an index that has its manifest"
        )
    try:
        manifest = json.loads(mpath.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise JevError(f"{mpath}: not JSON ({exc})") from exc
    corpus = manifest.get("corpus_hash")
    digest = manifest.get("digest")
    if not corpus or not digest:
        raise JevError(f"{mpath}: equivalence-index manifest missing corpus_hash and/or digest")
    if corpus != run_corpus_hash:
        raise JevError(
            f"{mpath}: index corpus_hash {corpus!r} differs from the run's {run_corpus_hash!r}; the "
            "index was built over a different corpus — point --equivalence-index at the matching index"
        )
    if not path.exists():
        raise JevError(f"{path}: equivalence-index file not found")
    lookup: dict[tuple, list[dict]] = {}
    n_rows = 0
    with open(path, encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise JevError(f"{path}:{line_no}: not JSON ({exc})") from exc
            work, citation, language = row.get("work"), row.get("citation"), row.get("language")
            wordings = row.get("wordings")
            if not (work and citation and language):
                raise JevError(f"{path}:{line_no}: index row missing work/citation/language")
            if not isinstance(wordings, list) or not wordings:
                raise JevError(f"{path}:{line_no}: index row has no wordings list")
            for w in wordings:
                if not isinstance(w, dict) or not w.get("version") or not isinstance(w.get("text"), str):
                    raise JevError(f"{path}:{line_no}: index wording missing version/text")
                rkey = (work, w["version"], language)
                if rkey in restricted_keys:
                    raise JevError(
                        f"{path}:{line_no}: index wording {rkey!r} is a RESTRICTED target; its text "
                        "must never reach the judge — this is a broken index (fail fast, independent "
                        "of the commit-time audit gate)"
                    )
            key = (work, citation, language)
            if key in lookup:
                raise JevError(f"{path}:{line_no}: duplicate index row for {key!r}; one row per (work, citation, language)")
            lookup[key] = wordings
            n_rows += 1
    row_count = manifest.get("row_count")
    if row_count is not None and row_count != n_rows:
        raise JevError(
            f"{mpath}: manifest row_count {row_count} != {n_rows} rows in {path}; index/manifest disagree"
        )
    return EquivalenceIndex(lookup=lookup, corpus_hash=corpus, digest=digest, row_count=row_count)


def summarize(path: Path) -> dict:
    """Counts + total spend of what has been judged. Empty/absent file → zeros. No network."""
    kinds: Counter[str] = Counter()
    refusals = 0
    n = 0
    total_cost = 0.0
    builds: set[str] = set()
    if path.exists():
        with open(path, encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    # A truncated last line is the realistic interrupt case the spec names;
                    # surface it on the clean error path, not as a raw traceback.
                    raise JevError(f"{path}:{line_no}: not JSON ({exc})") from exc
                n += 1
                if row.get("judge_model_resolved"):
                    builds.add(row["judge_model_resolved"])
                # equivalence lands as the flat `kind` field (when evaluated) or the
                # `equivalence: "not_evaluated"` sentinel (when no index was supplied).
                if row.get("kind"):
                    kinds[row["kind"]] += 1
                elif row.get("equivalence") == "not_evaluated":
                    kinds["not_evaluated"] += 1
                if _num(row.get("refusal_p")) and row["refusal_p"] >= 0.5:
                    refusals += 1
                cost = (row.get("usage") or {}).get("cost")
                if _num(cost):
                    total_cost += float(cost)
    return {
        "n": n,
        "kinds": dict(sorted(kinds.items())),
        "refusal_p_ge_0.5": refusals,
        "total_cost_usd": round(total_cost, 6),
        "judge_models": sorted(builds),
        "rubric_id": RUBRIC_ID,
    }


def load_provenance(judgments: Path, *, question_set_digest: str | None) -> dict:
    """Validate that a judgments sidecar binds to the answers being scored and return the
    resolved-build provenance to stamp into a run's summary (``score --judgments``). No network.

    Both the manifest **and the rows** are validated, so provenance can never be stamped for a pass
    that produced nothing (or a mismatched pass):

    - the sibling ``.manifest.json`` must exist, name this rubric, carry a non-empty resolved build,
      and record the question-set digest of the answers being scored;
    - the sidecar file must exist and hold **at least one** judgment, and every row must agree with
      the manifest's resolved build and question-set digest (via ``_load_existing``, the same row
      guard the resume path uses — a build- or set-mismatched / build-less row fails fast).

    A missing manifest, wrong rubric, absent build, question-set mismatch, missing/empty sidecar, or a
    row that disagrees with the pinned identity **fails fast**. This is an explicit opt-in: default
    ``score`` never reads an adjacent sidecar.

    NB: the manifest checks below parallel ``_load_manifest`` (the resume-path validator) on purpose —
    they are kept separate so provenance does not bind ``index_digest`` (see ``_load_manifest``).
    """
    mpath = _manifest_path(judgments)
    if not mpath.exists():
        raise JevError(
            f"{judgments}: no manifest ({mpath}); a judgments sidecar carries its build identity in a "
            "sibling .manifest.json — run `judge` to produce one"
        )
    try:
        manifest = json.loads(mpath.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise JevError(f"{mpath}: not JSON ({exc})") from exc
    if manifest.get("rubric_id") != RUBRIC_ID:
        raise JevError(f"{mpath}: rubric {manifest.get('rubric_id')!r} != {RUBRIC_ID!r}")
    resolved = manifest.get("judge_model_resolved")
    if not resolved:
        raise JevError(f"{mpath}: manifest has no judge_model_resolved; its build identity is unknown")
    if manifest.get("question_set_digest") != question_set_digest:
        raise JevError(
            f"{mpath}: judgments question-set digest {manifest.get('question_set_digest')!r} != the "
            f"answers' {question_set_digest!r}; these judgments are for a different question set"
        )
    # The manifest alone is not proof of verdicts: require the sidecar to exist and carry real rows,
    # each agreeing with the pinned build + question-set digest (reusing the resume row guard).
    if not judgments.exists():
        raise JevError(
            f"{judgments}: manifest present but the judgments file is missing; "
            "`score --judgments` needs the sidecar itself — run `judge`"
        )
    judged = _load_existing(judgments, pinned_build=resolved, pinned_qsd=question_set_digest,
                            require_verdict=True)
    if not judged:
        raise JevError(
            f"{judgments}: no judgments recorded; `score --judgments` needs a sidecar with at least "
            "one verdict before it can stamp a judge build into the summary"
        )
    return {"model_resolved": resolved, "rubric_id": manifest["rubric_id"]}
