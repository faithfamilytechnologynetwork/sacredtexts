"""Spec 52 — witness that the Uthmani↔Imla'i orthography rebaseline moved ONLY the containment
headline, and exactly on the registered cells, across EVERY committed run.

Sibling of ``test_contains_reference_rebaseline.py`` (which covers the first-run / tutorial headline
flip sets) and ``test_refusal_rebaseline.py``. This oracle owns the Spec-52-specific guarantees over
ALL five committed score files — including ``original-2026-10-21`` and the
``exp-arabic-prompts-2026-10-29`` A/B, which the other oracles do not cover:

1. **Similarity frozen everywhere.** The ``(exact, normalized, token_f1)`` projection SHA of each
   committed score file is UNCHANGED from the pre-#52 base (origin/main ``b93e881``). The fold lives
   only in the containment predicate (``fold_aware_contains``); ``normalize()`` and all equality
   submetrics are byte-stable, so generation's ANCHOR digest and the copyright audit are untouched.
2. **Clean superset.** For every retrieve_quote / complete_unit cell in every run,
   ``correct == (normalized OR contains_reference)`` and ``normalized == 1 ⇒ contains_reference == 1``
   — the fold can only ADD containment credit.
3. **Exactly the registered orthographic movers.** The cells the fold newly credits are precisely
   those with ``contains_reference == 1`` while the pre-#52 word-bounded ``bounded_contains`` is
   False — i.e. credited BY the orthography fold, not by pre-existing containment. Their per-run
   count is pinned, and every one is ``correct == 1`` (the fold never removes credit).
4. **The experiment recovers.** Under the fold the Arabic-prompt artifact is gone: both models in
   BOTH conditions of the exp A/B score 27/28, and 0 of 56 cells flip between en and ar.

Read-only; re-derives containment from the committed answers. Skips cleanly if evidence is absent.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from sacredbench.score import bounded_contains, fold_aware_contains, normalize

REPO_ROOT = Path(__file__).resolve().parents[2]

# (exact, normalized, token_f1) projection SHA-256, FROZEN from the pre-#52 committed scores
# (origin/main b93e881). MUST be reproduced byte-for-byte post-rebaseline — the fold touches no
# similarity tier. Keyed by score-file path (relative to runs/).
SIM_PROJECTION_SHA256 = {
    "tutorial-2026-10-11/scores.jsonl": "6dbf9a9c157c440f54428b8624f85a88f346f2f6c228a720812dd3d053565467",
    "original-2026-10-21/scores.jsonl": "581e0030c525b7d92d49bb66417ebd5d63d2154f7b4614310a608fd3c9c7b868",
    "first-run-2026-10-11/scores.jsonl": "8114b0d4fe14e9bde63e2c1147fc764995a39e4956987403e8aab6bea6bff3e2",
    "exp-arabic-prompts-2026-10-29/scores-ar.jsonl": "c369e76ad5d40baf819b523ced13d9fdabedbe5e84d55a8daeaeadf8912ca580",
    "exp-arabic-prompts-2026-10-29/scores-en.jsonl": "83d57ee5f3f14135022ddb51d93f3bd744e4887f80ef6948a5ce14735dab1259",
}

# Per-run count of cells the orthography fold newly credits (contains_reference=1 while the pre-#52
# bounded_contains is False). Hand-verified against each verse (Spec 52 review). Total = 58.
ORTHO_MOVER_COUNT = {
    "tutorial-2026-10-11": 20,
    "original-2026-10-21": 15,
    "first-run-2026-10-11": 0,
    "exp-arabic-prompts-2026-10-29/ar": 14,
    "exp-arabic-prompts-2026-10-29/en": 9,
}

_TEXT_TASKS = ("retrieve_quote", "complete_unit")


def _load(path: str):
    p = REPO_ROOT / "runs" / path
    if not p.exists():
        pytest.skip(f"{path} not present")
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def _answers(path: str):
    p = REPO_ROOT / "runs" / path
    if not p.exists():
        pytest.skip(f"{path} not present")
    return {
        (d["model_id"], d["question_id"]): (d["answer"], d["question"]["expected"])
        for d in (json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip())
    }


@pytest.mark.parametrize("path", list(SIM_PROJECTION_SHA256))
def test_similarity_projection_frozen(path):
    rows = _load(path)
    proj = sorted(
        (r["model_id"], r["question_id"], r["task"],
         r["metrics"].get("exact"), r["metrics"].get("normalized"), r["metrics"].get("token_f1"))
        for r in rows
    )
    digest = hashlib.sha256(json.dumps(proj, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    assert digest == SIM_PROJECTION_SHA256[path], (
        f"{path}: exact/normalized/token_f1 projection moved — the orthography fold must not touch "
        "any similarity tier (it lives only in fold_aware_contains)"
    )


@pytest.mark.parametrize("path", [
    "tutorial-2026-10-11/scores.jsonl", "original-2026-10-21/scores.jsonl",
    "first-run-2026-10-11/scores.jsonl",
])
def test_headline_is_a_clean_superset(path):
    for r in _load(path):
        if r["task"] not in _TEXT_TASKS:
            continue
        m = r["metrics"]
        if "contains_reference" not in m:
            continue
        if m.get("normalized") == 1:
            assert m["contains_reference"] == 1, "normalized=1 must imply contains_reference=1"
        assert m["correct"] == int(bool(m.get("normalized")) or bool(m["contains_reference"]))


@pytest.mark.parametrize("run,scores,answers", [
    ("tutorial-2026-10-11", "tutorial-2026-10-11/scores.jsonl", "tutorial-2026-10-11/answers.jsonl"),
    ("original-2026-10-21", "original-2026-10-21/scores.jsonl", "original-2026-10-21/answers.jsonl"),
    ("first-run-2026-10-11", "first-run-2026-10-11/scores.jsonl", "first-run-2026-10-11/answers.jsonl"),
])
def test_orthographic_movers_are_exactly_the_registered_count(run, scores, answers):
    ans = _answers(answers)
    movers = []
    for r in _load(scores):
        if r["task"] not in _TEXT_TASKS:
            continue
        m = r["metrics"]
        if m.get("contains_reference") != 1:
            continue
        answer, expected = ans[(r["model_id"], r["question_id"])]
        target = expected["text"]
        # credited by the fold specifically: fold_aware_contains holds but the pre-#52 word-bounded
        # bounded_contains does not. (A plain containment flip has bounded_contains True and is NOT
        # an orthographic mover.)
        if normalize(target) and fold_aware_contains(answer, target) and not bounded_contains(answer, target):
            movers.append((r["model_id"], r["question_id"]))
            assert m["correct"] == 1, "a fold-credited cell must be correct (the fold only adds credit)"
    assert len(movers) == ORTHO_MOVER_COUNT[run], (
        f"{run}: {len(movers)} orthographic movers, expected {ORTHO_MOVER_COUNT[run]} — the fold "
        "credited a different set than was registered + hand-verified"
    )


def test_exp_arabic_prompt_artifact_is_resolved():
    # The motivating A/B: under the fold, both models in BOTH conditions score 27/28, and no cell
    # flips between en and ar — the ~8-11pt Arabic-prompt drop was entirely a scorer artifact.
    en = {(r["model_id"], r["question_id"]): r for r in _load("exp-arabic-prompts-2026-10-29/scores-en.jsonl")}
    ar = {(r["model_id"], r["question_id"]): r for r in _load("exp-arabic-prompts-2026-10-29/scores-ar.jsonl")}
    assert en.keys() == ar.keys() and len(en) == 56
    for cond in (en, ar):
        per_model: dict[str, int] = {}
        for (mid, _qid), r in cond.items():
            per_model[mid] = per_model.get(mid, 0) + int(r["metrics"]["outcome"] == "correct")
        assert set(per_model.values()) == {27}, f"expected 27 correct/model, got {per_model}"
    flips = sum(1 for k in en if en[k]["metrics"]["outcome"] != ar[k]["metrics"]["outcome"])
    assert flips == 0, f"{flips} en↔ar outcome flips survived the fold (expected 0)"
