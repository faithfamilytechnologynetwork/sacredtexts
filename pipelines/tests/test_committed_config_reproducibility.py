"""Committed panel config ↔ committed run reproducibility (regression guard for PR #31).

A committed run under ``runs/`` is finished, copyright-audited evidence. Some committed runs
ship with the committed panel config that reproduces them — scoring the run with
``score --config <that file>`` cross-checks each model's panel fingerprint against the
fingerprint stored on the run's answers (collect.py / score.py), and a drift between the two
makes that command fail (`collected under panel identity ... but --config now maps it to ...`).

So a committed config must NOT drift away from the run it reproduces. This is exactly what
bit PR #31: adding ``temperature: 0`` to a committed config appends ``|t=0.0`` to every
fingerprint, which no longer matches the no-temperature fingerprints baked into the committed
answers. These configs therefore keep temperature UNSET (a commented example line documents
how to pin it in a fresh run).

This test is the standing guard: for every committed-run ↔ committed-config pair, the set of
fingerprints the config produces must equal the set of fingerprints stored on that run's
answers. Add a pair here whenever a run ships with its reproduction config.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sacredbench.collect import _panel_fingerprint
from sacredbench.config import load_config

REPO_ROOT = Path(__file__).resolve().parents[2]

# run directory (under runs/) -> the committed panel config that reproduces it.
COMMITTED_PAIRS = {
    "runs/tutorial-2026-10-11": "configs/models.example.yaml",
    "runs/original-2026-10-21": "configs/models.openrouter.yaml",
}


def _run_fingerprints(answers_path: Path) -> set[str]:
    fps: set[str] = set()
    with open(answers_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                fps.add(json.loads(line)["panel_fingerprint"])
    return fps


@pytest.mark.parametrize("run_dir, config_path", sorted(COMMITTED_PAIRS.items()))
def test_committed_config_fingerprints_match_run(run_dir: str, config_path: str):
    answers = REPO_ROOT / run_dir / "answers.jsonl"
    config = REPO_ROOT / config_path
    assert answers.exists(), f"committed run missing: {answers}"
    assert config.exists(), f"committed config missing: {config}"

    cfg = load_config(config)
    config_fps = {_panel_fingerprint(m) for m in cfg.models}
    run_fps = _run_fingerprints(answers)

    # Set equality, not subset: a config that drops/adds a model, or whose fingerprints drift
    # (e.g. a stray temperature: 0 appending |t=0.0), fails here before it can break
    # `score --config` against the committed run.
    assert config_fps == run_fps, (
        f"{config_path} no longer reproduces {run_dir}: "
        f"config-only fingerprints {sorted(config_fps - run_fps)}, "
        f"run-only fingerprints {sorted(run_fps - config_fps)}"
    )
