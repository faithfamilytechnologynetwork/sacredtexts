"""Spec 48 — non-circular witness that the refusal rebaseline moved ONLY the registered cells.

Sibling of ``test_contains_reference_rebaseline.py``. The Spec-48 change reclassifies 5 hedged-but-
delivering tutorial cells from ``refused`` to ``incorrect``. Re-pinning ``REFUSED_SET_SHA256`` from
the *post*-change scores (as the Spec-15 guard does) proves the matcher reproduces the committed
file, but it cannot witness that *nothing else* moved — the committed file is what this PR
regenerated. This oracle is that witness, over the regenerated ``tutorial-2026-10-11`` evidence:

1. **Frozen PRE-change projections** — SHA-256 of the canonical ``(model_id, question_id) ->
   outcome`` and ``-> correct`` projections, captured via ``git show HEAD:…`` *before* the scores
   were regenerated (HEAD being the pre-fix commit at authoring time).
2. **Exact outcome transform** — applying ``refused -> incorrect`` to EXACTLY the 5 registered cells
   of the pre-change outcomes reproduces the post-change outcomes, cell for cell (not an aggregate:
   compensating moves can preserve a count).
3. **correct & similarity untouched** — the ``correct`` projection SHA is unchanged (no headline
   moved) and the ``(exact, normalized, token_f1)`` similarity projection SHA is unchanged (pinned
   in ``test_contains_reference_rebaseline.py``; the refusal rebaseline touches only ``outcome``).

Read-only; skips cleanly if the run evidence is absent.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
RUN = "tutorial-2026-10-11"

# The 5 cells reclassified refused -> incorrect (delivered-as-answer; architect-approved 2026-10-29).
FLIP_SET = {
    ("haiku-search", "retrieve_quote-e2d74279aaf0"),
    ("opus-search", "retrieve_quote-349b0b401f72"),
    ("opus-search", "retrieve_quote-b33e7e040058"),
    ("opus-search", "retrieve_quote-d0239d95ae29"),
    ("opus-search", "retrieve_quote-d4c3bda0b400"),
}

# Captured from the PRE-change committed scores.jsonl (git HEAD before regeneration), Spec 48.
PRECHANGE_OUTCOME_SHA256 = "99a724e178ed6e58d36f5614997390c7bb2103fb86075da4c8b0097cdb8a86ef"
PRECHANGE_CORRECT_SHA256 = "de3422497e2eb90fa334184c9a72f6bf823fc106ebd5166af078ae5b46017c98"


def _load_scores():
    p = REPO_ROOT / "runs" / RUN / "scores.jsonl"
    if not p.exists():
        pytest.skip(f"{RUN} evidence not present")
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def _proj_sha(rows, fields):
    items = sorted((r["model_id"], r["question_id"], *[r["metrics"].get(f) for f in fields]) for r in rows)
    return hashlib.sha256(json.dumps(items, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def test_correct_projection_unchanged():
    # no headline `correct` bit moved — the flips were refused(0) -> incorrect(0)
    assert _proj_sha(_load_scores(), ["correct"]) == PRECHANGE_CORRECT_SHA256


def test_outcome_transform_is_exactly_the_flip_set():
    # reconstruct the pre-change outcomes by UN-applying the registered flip, then check the SHA:
    # every registered cell is `incorrect` post-change (was `refused`), and un-flipping them must
    # reproduce the frozen pre-change projection — so no other cell's outcome moved.
    scores = _load_scores()
    post = {(s["model_id"], s["question_id"]): s["metrics"]["outcome"] for s in scores}
    for key in FLIP_SET:
        assert post[key] == "incorrect", f"{key} is not `incorrect` post-rebaseline ({post.get(key)})"
    reconstructed = [
        {
            "model_id": s["model_id"],
            "question_id": s["question_id"],
            "metrics": {
                "outcome": "refused"
                if (s["model_id"], s["question_id"]) in FLIP_SET
                else s["metrics"]["outcome"]
            },
        }
        for s in scores
    ]
    assert _proj_sha(reconstructed, ["outcome"]) == PRECHANGE_OUTCOME_SHA256, (
        "un-flipping the 5 registered cells did not reproduce the pre-change outcome projection — "
        "an unregistered outcome moved in the rebaseline"
    )
