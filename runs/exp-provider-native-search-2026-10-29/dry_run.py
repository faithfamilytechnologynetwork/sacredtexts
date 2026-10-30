"""Keyless dry-run for the provider-native search experiment (#54).

Proves the harness is wired correctly WITHOUT any API call or key: the panel loads, the
questions load, the search-on/off arms carry distinct panel fingerprints, and the cell plan
is exactly 56 x 4 = 224 (2 models x search on/off; gemini deferred). Makes no network call.

    uv --project pipelines run python runs/exp-provider-native-search-2026-10-29/dry_run.py
"""

from __future__ import annotations

from pathlib import Path

from sacredbench.collect import _panel_fingerprint
from sacredbench.config import load_config
from sacredbench.generate import load_questions, question_set_digest

HERE = Path(__file__).resolve().parent
EXPECTED_QUESTIONS = 56
EXPECTED_CELLS = 224  # 56 questions x 4 entries (2 models x search on/off; gemini deferred)


def main() -> None:
    cfg = load_config(HERE / "models.yaml")
    questions = load_questions(HERE / "questions.jsonl")

    if len(questions) != EXPECTED_QUESTIONS:
        raise SystemExit(f"FAIL: expected {EXPECTED_QUESTIONS} questions, got {len(questions)}")
    cells = len(questions) * len(cfg.models)
    if cells != EXPECTED_CELLS:
        raise SystemExit(f"FAIL: expected {EXPECTED_CELLS} cells, got {cells}")

    # the two arms of each model must be distinct panel identities, or the committed panel
    # would collapse search-on and -off into one row
    fps = {m.id: _panel_fingerprint(m) for m in cfg.models}
    if len(set(fps.values())) != len(fps):
        raise SystemExit(f"FAIL: panel fingerprints are not all distinct: {fps}")

    print(f"question set digest: {question_set_digest(questions)}")
    print(f"questions: {len(questions)}  x  models: {len(cfg.models)}  =  {cells} cells\n")
    print(f"{'id':<16}{'provider':<10}{'model':<30}{'search':<8}fingerprint")
    for m in cfg.models:
        search = "on" if "web_search" in m.tools else "off"
        print(f"{m.id:<16}{m.provider:<10}{m.model:<30}{search:<8}{fps[m.id]}")
    print("\nOK: harness validates keyless. Live collect needs OPENROUTER_API_KEY.")


if __name__ == "__main__":
    main()
