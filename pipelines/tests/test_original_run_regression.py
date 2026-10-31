"""Regression guard for the committed Spec-26 `original-2026-10-21` evidence.

This run is the current reference evidence (four templates, 17 original-language-only texts,
three-model panel) and the **generation-invariance anchor** that replaced the retired first-run
generator guard (`test_first_run_regression.py`). Two invariants:

- **Scoring invariance (always runs):** re-scoring the committed `answers.jsonl` to a scratch
  path reproduces the committed `scores.jsonl` byte-for-byte — proof that scoring changes did
  not move the only committed evidence that exercises Arabic/Aramaic `normalize()`, the
  leading-stance `parse_yes_no`, and `cite_passage`/`complete_unit` over 1,428 real answers.
- **Generation invariance (skips if `texts/standardized/` is absent, i.e. in a fresh clone /
  CI where the rebuilt corpus is gitignored):** regenerating the question set from the committed
  manifest's own inputs/seed/per_text/negatives_share reproduces a pinned question-set digest.
  The pin is anchored to the CURRENT corpus (``ANCHOR_CORPUS_HASH``/``ANCHOR_DIGEST`` below):
  while the corpus stood at the run's own ``corpus_hash`` this reproduced the run's digest
  `de65959a99dea9b3` (what Phase 2's retirement note promised was "digest-pinned here"); each
  sanctioned corpus update re-pins the anchor pair.

Both write only to tmp paths; neither touches the committed evidence.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import hashlib

from sacredbench import catalogue as cat
from sacredbench import cli
from sacredbench.score import _citation_candidates, score_file

REPO_ROOT = Path(__file__).resolve().parents[2]
RUN = REPO_ROOT / "runs" / "original-2026-10-21"
PINNED_DIGEST = "de65959a99dea9b3"

# Generation-invariance anchor over the CURRENT corpus. The committed run reproduced its own
# digest while the corpus stood at its manifest's corpus_hash (5ae493e7e249575c); a sanctioned
# corpus update legitimately moves both values (2026-10-28: Talmud WD refresh — Meilah/Niddah/
# Tamid added, one-line Berakhot-en correction; Spec 50: Sri Guru Granth Sahib added, 18 texts,
# 504 questions; Spec 63: the Dhammapada added, 19 texts, 532 questions; Spec 64: Bhagavad Gita
# added, 20 texts, 560 questions, Besant's English outside the pool). On such an update, re-pin
# BOTH constants from
# a fresh `generate` with the run manifest's params and rebuild the committed FAccT card
# (`python -m sacredbench facct runs/original-2026-10-21` — only selected_corpus_hash moves;
# a text added after the run leaves the card unchanged, Spec 50).
# Never loosen these assertions and never touch the committed run evidence itself.
ANCHOR_CORPUS_HASH = "65bb68f118d63112"  # texts/ as of Spec 64 (Bhagavad Gita added)
ANCHOR_DIGEST = "93b71460742a8ecd"  # generate over that corpus with the run's params

# Pre-registered cite_passage decline survey (Spec 26 round-1b, fold B). Every cite_passage answer
# that yields ZERO citation candidates was hand-surveyed: a first-person inability to cite
# ("I can't confirm/pinpoint the number") is a decline and its phrasing was added to
# _DECLINE_CUES_RAW; a confident non-existence claim ("Not found in the KJV") or a bare book-name
# attempt stays incorrect. This pins the surveyed population by count + SHA so any change to those
# committed answers forces a fresh survey rather than silently shifting the decline set.
SURVEY_COUNT = 24
SURVEY_SHA256 = "8244e9fb6c6b4d44ed067c3e0f6a75504f6bf28031259fe3ec334a90f24c5060"


def test_rescoring_committed_original_run_reproduces_scores(tmp_path):
    answers = RUN / "answers.jsonl"
    committed = RUN / "scores.jsonl"
    if not answers.exists() or not committed.exists():
        pytest.skip("original-2026-10-21 evidence not present")
    out = tmp_path / "scores.jsonl"
    score_file(answers, out)  # no roster/panel needed to reproduce per-answer scores
    # byte-for-byte, order included (score_file preserves input-row order).
    assert out.read_text(encoding="utf-8") == committed.read_text(encoding="utf-8")


def test_committed_facct_card_matches_the_run():
    # the committed FAccT card (Spec 32) must equal a fresh build from the committed evidence, so a
    # sanctioned rebaseline that moved scores.jsonl / summary.json — or a CARD_PROSE edit — without
    # regenerating the card is caught here rather than shipping a card that contradicts its own run.
    # REMEDY when this fails: regenerate the card
    #   (`python -m sacredbench facct runs/original-2026-10-21`), do NOT loosen the assertion.
    facct_json = RUN / "facct.json"
    if not facct_json.exists() or not (REPO_ROOT / "texts" / "raw").exists():
        pytest.skip("committed facct card or raw tree not present")
    from sacredbench.facct import build_facct, report_markdown

    rebuilt = build_facct(RUN)
    assert json.loads(facct_json.read_text(encoding="utf-8")) == rebuilt  # facct.json
    assert (RUN / "facct.md").read_text(encoding="utf-8") == report_markdown(rebuilt)  # facct.md


def test_cite_passage_decline_survey_is_pinned():
    """The hand-surveyed zero-citation-candidate cite_passage set is fixed (count + SHA)."""
    answers = RUN / "answers.jsonl"
    if not answers.exists():
        pytest.skip("original-2026-10-21 evidence not present")
    rows = [json.loads(l) for l in answers.open(encoding="utf-8") if l.strip()]
    zero = [
        r for r in rows
        if r["task"] == "cite_passage"
        and not _citation_candidates(r.get("answer") or "", r["question"]["expected"]["citation"])
    ]
    assert len(zero) == SURVEY_COUNT
    ids = sorted(f"{r['model_id']}\0{r['question_id']}\0{r.get('answer') or ''}" for r in zero)
    sha = hashlib.sha256("\n".join(ids).encode()).hexdigest()
    assert sha == SURVEY_SHA256


def test_regenerating_original_run_reproduces_digest(tmp_path, monkeypatch):
    """Regenerate with the committed manifest's own params and match the anchor digest.

    The anchor is the current corpus (ANCHOR_CORPUS_HASH/ANCHOR_DIGEST above), not the
    committed run's own corpus state: generator-code drift still trips the digest assert,
    while a deliberate corpus update trips the corpus-hash assert and demands a re-pin.
    """
    manifest_path = RUN / "questions.jsonl.manifest.json"
    standardized = REPO_ROOT / "texts" / "standardized"
    if not manifest_path.exists() or not standardized.exists():
        pytest.skip("original-2026-10-21 manifest or rebuilt corpus not present")
    m = json.loads(manifest_path.read_text(encoding="utf-8"))
    # The committed manifest is self-consistent with the pinned digest.
    assert m["question_set_digest"] == PINNED_DIGEST

    # Drive the real CLI generate path from the manifest's recorded inputs — relative
    # catalogue paths (cat.RAW_ROOT / cat.STANDARDIZED_ROOT) resolve from the repo root.
    monkeypatch.chdir(REPO_ROOT)
    out = tmp_path / "questions.jsonl"
    cli.generate(
        inputs=[Path(p) for p in m["inputs"]],
        out=out,
        per_text=m["per_text"],
        tasks=None,  # the committed run used no --tasks subset (all four templates)
        seed=m["seed"],
        negatives_share=m["negatives_share"],
        raw_root=cat.RAW_ROOT,
        standardized_root=cat.STANDARDIZED_ROOT,
        include_restricted=False,
    )
    regenerated = json.loads(
        (tmp_path / "questions.jsonl.manifest.json").read_text(encoding="utf-8")
    )
    assert regenerated["corpus_hash"] == ANCHOR_CORPUS_HASH, (
        "the corpus moved — if this was a sanctioned texts/ update, re-pin "
        "ANCHOR_CORPUS_HASH and ANCHOR_DIGEST (see the comment at the anchors) "
        "and rebuild the committed FAccT card; otherwise find what changed texts/"
    )
    assert regenerated["question_set_digest"] == ANCHOR_DIGEST, (
        "generate produced a different question set for a fixed corpus + params — "
        "generator-code drift; this must be deliberate and re-pinned"
    )
