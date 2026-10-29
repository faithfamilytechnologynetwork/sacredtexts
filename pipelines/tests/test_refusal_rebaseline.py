"""Spec 48 — witness that the 5 hedged-but-delivering tutorial cells are reclassified OUT of
``refused``. Current-state invariant (stacking-robust), re-pinned for the Spec-52 rebaseline.

HISTORY / what this file used to prove, and where that proof now lives
---------------------------------------------------------------------
At its authoring (PR #55, Spec 48) this oracle froze two PRE-change projection SHAs — the
``(model_id, question_id) -> outcome`` and ``-> correct`` projections of the pre-#48 committed
scores — and proved, by exact reconstruction, that the refusal rebaseline moved ONLY ``outcome``
for EXACTLY these 5 cells (``refused -> incorrect``) and touched NO ``correct`` bit. That was a
witness of #48 **in isolation**.

Spec 52 (the Uthmani↔Imla'i orthography fold) then stacked a SECOND sanctioned rebaseline on the
SAME committed ``tutorial-2026-10-11`` scores: it credits 20 Imla'i retrieve_quote cells
(``incorrect -> correct``), one of which is ``haiku-search retrieve_quote-e2d74279aaf0`` — a
verbatim Imla'i answer whose full journey is ``refused`` (pre-#48) → ``incorrect`` (#48,
delivered-not-refusal) → ``correct`` (#52). Because the committed file now reflects BOTH
rebaselines, #48's isolation SHAs can no longer be reconstructed from it, and the ``correct``
projection legitimately moved. Re-pinning those SHAs to the current file would make them assert
"current == current" (circular); un-applying both rebaselines would couple this test to #52's flip
set and grow quadratically with every future rebaseline. So the isolation asserts are RETIRED here.

Their proof is preserved, unchanged, in: **PR #55** (the Spec-48 merge) and its diff; the Spec-48
**review doc** (``codev/reviews/48-refusal-classifier-false-posit.md``); and the **pre-#52 commit**
on ``main`` (``b93e881``), whose ``runs/tutorial-2026-10-11/scores.jsonl`` is the post-#48 /
pre-#52 state the original SHAs were frozen against.

What THIS file now witnesses (current committed evidence, robust to future stacking):
1. all 5 registered cells are reclassified OUT of ``refused`` (#48's durable claim);
2. the triple-penalty cell is specifically ``correct`` and the other 4 ``incorrect`` (makes the
   #48×#52 composition explicit, not silent);
3. that #52 moved NO refusals is pinned by ``REFUSED_SET_SHA256`` in
   ``test_contains_reference_rebaseline.py`` (passes unchanged); the full #52 transform is pinned
   by ``test_orthography_rebaseline.py``.

Read-only; skips cleanly if the run evidence is absent.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
RUN = "tutorial-2026-10-11"

# The 5 cells Spec 48 reclassified refused -> (answered) (delivered-as-answer; architect-approved
# 2026-10-29). Post-Spec-52, one of them is further promoted to `correct` (see below).
FLIP_SET = {
    ("haiku-search", "retrieve_quote-e2d74279aaf0"),  # #52: now `correct` (verbatim Imla'i)
    ("opus-search", "retrieve_quote-349b0b401f72"),
    ("opus-search", "retrieve_quote-b33e7e040058"),
    ("opus-search", "retrieve_quote-d0239d95ae29"),
    ("opus-search", "retrieve_quote-d4c3bda0b400"),
}
# The one cell promoted incorrect -> correct by the Spec-52 orthography fold (the triple-penalty
# anecdote: honest decline mis-scored as refused, then incorrect, finally credited).
PROMOTED_TO_CORRECT = ("haiku-search", "retrieve_quote-e2d74279aaf0")


def _load_scores():
    p = REPO_ROOT / "runs" / RUN / "scores.jsonl"
    if not p.exists():
        pytest.skip(f"{RUN} evidence not present")
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def test_registered_cells_are_not_refused():
    # #48's durable claim: every one of the 5 is reclassified OUT of refused (delivered, not a
    # refusal). Robust to the Spec-52 fold, which only promotes WITHIN `answered`, never to refused.
    post = {(s["model_id"], s["question_id"]): s["metrics"]["outcome"] for s in _load_scores()}
    for key in FLIP_SET:
        assert key in post, f"{key} absent from committed scores"
        assert post[key] != "refused", f"{key} is `refused` — the Spec-48 reclassification regressed"


def test_triple_penalty_cell_is_correct_and_others_incorrect():
    # Makes the #48 × #52 composition explicit: the verbatim-Imla'i cell is `correct` (Spec 52),
    # the other four remain `incorrect` (delivered but not the reference text, no orthographic match).
    post = {(s["model_id"], s["question_id"]): s["metrics"]["outcome"] for s in _load_scores()}
    assert post[PROMOTED_TO_CORRECT] == "correct"
    for key in FLIP_SET - {PROMOTED_TO_CORRECT}:
        assert post[key] == "incorrect", f"{key} expected `incorrect`, got {post[key]}"
