"""Issue #50 part 2 — witness that the Gurmukhi/Devanagari/Pali normalize fix is a NO-FLIP rebaseline.

Sibling of ``test_orthography_rebaseline.py``. Every answer in every committed run is re-scored live
and the full metrics dict of each row is hashed. The pin was taken from the pre-fix scorer, so any
metric of any committed row that moves, ``token_f1`` included, fails here. A global Pali recompose
moved three ``token_f1`` values in ``original-2026-10-21`` (English answers naming Bukhārī); that is
why the recompose is scoped by the reference.

Read-only. Skips cleanly if the evidence is absent.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from sacredbench.score import score_answer

REPO_ROOT = Path(__file__).resolve().parents[2]
ROWS = 2620
PROJECTION_SHA256 = "08c0857d002fbe2b847b82781f7f31186596990870966062be8271e91fab2945"


def test_every_committed_row_scores_exactly_as_before_the_fix():
    files = sorted((REPO_ROOT / "runs").rglob("answers*.jsonl"))
    if not files:
        pytest.skip("committed run evidence not present")
    h = hashlib.sha256()
    rows = 0
    for path in files:
        for line in path.open(encoding="utf-8"):
            a = json.loads(line)
            metrics = score_answer(a["task"], a["answer"], a["question"]["expected"])
            h.update(json.dumps(metrics, sort_keys=True).encode("utf-8"))
            rows += 1
    assert rows == ROWS
    assert h.hexdigest() == PROJECTION_SHA256
