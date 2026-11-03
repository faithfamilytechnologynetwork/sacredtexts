"""Issue #95 — witness that verify_source now reads a yes/no verdict given in a language other than
the cell's, and that this moves EXACTLY the pre-registered cells, only out of ``refused``.

``parse_yes_no`` used to read a native word only on its own language's cell, so Punjabi ``ਨਹੀਂ`` on
a Pali cell or Syriac ``ܠܐ`` on a Hebrew cell was ``refused``. Now every non-Latin native word is
read on every cell (the Latin Pali ``na``/``āma`` stays gated to ``pi``), the stand-alone rule
unchanged. The same change adds Punjabi ``ਹਾਂ ਜੀ`` (polite yes) and Sanskrit ``नास्ति`` (no).

The registered set was derived by running the pre-#95 and #95 parsers over every committed answer
(``runs/**``) and is pinned here by identity, so a compensating add/remove swap cannot pass:

- 65 cells in committed ``scores.jsonl``, all ``refused`` there: 48 → correct, 17 → incorrect
  (44 cross-language, 5 ``ਹਾਂ ਜੀ``, 16 ``नास्ति`` — 15 of them gemma's "no" to an expected yes).
- 20 cells in ``gpt-oss-20b/.../buddhism/.../prompt-english``, collected but not yet scored.
- ``runs/archive``: none. No cell that already had a verdict changes.

The committed scores are NOT rewritten by #95 (the rerun is rescored under the final contract), so
the scan below accepts a registered cell as either still ``refused`` (pre-rescore) or already at its
registered outcome (post-rescore). Read-only; skips cleanly if the run evidence is absent.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pytest

from sacredbench.score import score_answer

RUNS = Path(__file__).resolve().parents[2] / "runs"

# answers folder (relative to runs/) -> {question_id: outcome under #95}
FLIPS: dict[str, dict[str, str]] = {
    "argon/base/sikhism/native/population/prompt-english": {  # ਹਾਂ ਜੀ on pa cells
        "0cc9e6de9262c40d": "correct", "be54645995594165": "correct", "be8a2d1aea62c4ce": "correct",
        "f4013fa11bc896a5": "correct", "f4ac1501c349dc14": "correct",
    },
    "deepseek-v4-pro/base/hinduism/native/population/prompt-english": {
        "cc142136eb66b273": "correct",
    },
    "deepseek-v4-pro/base/sikhism/native/population/prompt-english": {
        "1aa6746f1fc22fd6": "correct",
    },
    "gemma-31b/base/buddhism/native/population/prompt-english": {
        "3456a937cd425165": "correct", "43ea0b3e7a3ceaa1": "correct", "6c640c13353d9c54": "correct",
        "990a650deb71defd": "correct", "dbfb223b7bdd1869": "correct", "de3c0275d9aaf7df": "correct",
        "fdb48ed6544d82f8": "correct",
    },
    "gemma-31b/base/hinduism/native/population/prompt-english": {  # नास्ति on sa cells, + ਨਹੀਂ
        "098b4e996b67d7af": "correct", "0ae81b8046869dec": "correct",
        "0b1497819e8787de": "incorrect", "0c38e8158dd48ead": "incorrect",
        "10642635b5cc3456": "incorrect", "138ca95dcbb1cc4a": "incorrect",
        "1bf456e20feaa9ee": "incorrect", "1c7778747163ad02": "incorrect",
        "2fc4f66c3b499820": "incorrect", "42dc0d16da558321": "incorrect",
        "6c1d6957ded3e11e": "incorrect", "77b490b14bc1df3b": "incorrect",
        "8b68540cf4f08558": "incorrect", "a9ccd5c6a893ff1a": "incorrect",
        "b10269bd067b9261": "incorrect", "f2482c1570af286d": "incorrect",
        "fe4b3324549b1cee": "incorrect",
    },
    "gpt-oss-20b/base/buddhism/native/population/prompt-english": {  # not yet scored
        "227c87bb0a734f40": "correct", "2ed1ee0e0e1c4e58": "incorrect",
        "31704a379a6e0f7c": "correct", "43ea0b3e7a3ceaa1": "correct",
        "5d4dd91aa848e033": "incorrect", "6c640c13353d9c54": "incorrect",
        "81e663bef8230cbe": "incorrect", "867cabe22f6246b7": "correct",
        "8a58d1b5453c3279": "incorrect", "990a650deb71defd": "correct",
        "ac6c9687c82f9242": "correct", "af1f4a3526531ed6": "correct",
        "afea9265631b31bd": "incorrect", "ca844064e090827a": "correct",
        "d5479040959b4e59": "correct", "dbfb223b7bdd1869": "correct", "de3c0275d9aaf7df": "correct",
        "f09abdf191b1e4bf": "correct", "f76ec9ea39fa9582": "incorrect",
        "fdb48ed6544d82f8": "incorrect",
    },
    "gpt-oss-20b/base/hinduism/native/population/prompt-english": {
        "098b4e996b67d7af": "correct", "254ace3a398888fb": "correct", "6b0e7e43160ef97b": "correct",
    },
    "gpt-oss-20b/base/judaism/native/population/prompt-english": {  # Syriac ܠܐ on a he cell
        "6840ae7b70f63f33": "incorrect",
    },
    "gpt-oss-20b/base/sikhism/native/population/prompt-english": {  # Hebrew לא on pa cells
        "7d2ca992f5db1506": "correct", "832fc14302104c3f": "correct", "e2f1279d93565463": "correct",
        "ed4351efd933232b": "correct",
    },
    "haiku/base/buddhism/native/population/prompt-english": {
        "de3c0275d9aaf7df": "correct",
    },
    "luna/base/buddhism/native/population/prompt-english": {
        "31704a379a6e0f7c": "correct", "867cabe22f6246b7": "correct", "990a650deb71defd": "correct",
        "af1f4a3526531ed6": "correct", "ca844064e090827a": "correct", "d5479040959b4e59": "correct",
        "dbfb223b7bdd1869": "correct", "de3c0275d9aaf7df": "correct", "f09abdf191b1e4bf": "correct",
    },
    "luna/base/buddhism/native/population/prompt-native": {
        "04d77928dac7cc46": "correct", "4ce53397e6afc1c7": "correct",
    },
    "luna/base/hinduism/native/population/prompt-english": {
        "098b4e996b67d7af": "correct", "254ace3a398888fb": "correct", "6b0e7e43160ef97b": "correct",
        "7487e4787084051b": "correct", "98ce624e655c3d03": "correct",
    },
    "luna/base/judaism/native/population/prompt-english": {
        "16483a19c77ad1df": "incorrect", "6c6606b3b18b3fab": "correct",
        "f402424ffd6bc15e": "correct",
    },
    "sonnet/base/hinduism/native/population/prompt-english": {
        "254ace3a398888fb": "correct",
    },
    "terra/base/buddhism/native/population/prompt-english": {
        "ac6c9687c82f9242": "correct", "af1f4a3526531ed6": "correct", "d5479040959b4e59": "correct",
        "dbfb223b7bdd1869": "correct", "de3c0275d9aaf7df": "correct",
    },
}


def _verify_answers(folder: Path) -> dict[tuple[str, str], dict] | None:
    """The folder's verify_source answers by ``(model_id, question_id)``; ``None`` if it has none."""
    path = folder / "answers.jsonl"
    if not path.exists():
        return None
    rows = (json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    return {(d["model_id"], d["question_id"]): d for d in rows if d["task"] == "verify_source"}


def _outcome(d: dict) -> dict:
    q = d["question"]
    return score_answer("verify_source", d["answer"] or "", q["expected"], language=q["source"]["language"])


def test_registered_set_size():
    outcomes = Counter(o for cells in FLIPS.values() for o in cells.values())
    assert outcomes == {"correct": 60, "incorrect": 25}


@pytest.mark.parametrize("folder", sorted(FLIPS))
def test_registered_cells_are_graded_as_registered(folder):
    answers = _verify_answers(RUNS / folder)
    if answers is None:
        pytest.skip(f"{folder} evidence not present")
    model = folder.split("/", 1)[0]
    for qid, outcome in FLIPS[folder].items():
        metrics = _outcome(answers[(model, qid)])
        assert metrics["parsed"] is not None, (folder, qid)
        assert metrics["outcome"] == outcome, (folder, qid, metrics)


def test_only_registered_cells_move_and_only_out_of_refused():
    # Re-derive every committed verify_source score (runs/archive included) from its answer. A cell
    # may differ from its committed outcome only if it is registered, committed `refused`, and now at
    # its registered outcome: nothing else moves, and nothing moves into `refused` or from correct to
    # incorrect. A score file without a sibling answers.jsonl cannot be re-derived and is passed over.
    scanned = 0
    for scores in sorted(RUNS.glob("**/scores.jsonl")):
        answers = _verify_answers(scores.parent)
        if answers is None:
            continue
        folder = str(scores.parent.relative_to(RUNS))
        for line in scores.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if row["task"] != "verify_source":
                continue
            key = (row["model_id"], row["question_id"])
            assert key in answers, f"{folder}: scored verify_source cell {key} has no answer row"
            scanned += 1
            committed = row["metrics"]["outcome"]
            now = _outcome(answers[key])["outcome"]
            if now != committed:
                assert committed == "refused", (folder, row["question_id"], committed, now)
                assert FLIPS.get(folder, {}).get(row["question_id"]) == now, (folder, row["question_id"])
    if not scanned:
        pytest.skip("no committed verify_source scores present")
