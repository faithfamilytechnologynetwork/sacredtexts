"""Build the 56-question subset for the provider-native search experiment (#54).

Takes the 28 Qur'an + 28 Sahih al-Bukhari questions from the committed
`runs/original-2026-10-21/questions.jsonl` and writes them **verbatim** to
`questions.jsonl` in this run dir. The prompts, citations, expected ground truth, ids,
and source are byte-identical to the committed set — the search arm must ask exactly the
questions the committed benchmark asks, so the only delta across arms is search on/off.

Oracle: the written subset is reloaded and asserted equal (dataclass equality) to the
filtered originals, and the per-work counts are asserted to be exactly 28 + 28. Any drift
fails loud.

Run from the repo root (sacredbench on the path):

    uv --project pipelines run python runs/exp-provider-native-search-2026-10-29/build_questions.py
"""

from __future__ import annotations

from pathlib import Path

from sacredbench.generate import load_questions, write_questions

# The two texts under test: Qur'an carries the orthography findings (#52); Sahih al-Bukhari
# is our largest refusal effect. These are the `source.work` values in the committed set.
WORKS = {"The Qur'an", "Sahih al-Bukhari"}
EXPECTED_PER_WORK = 28

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SRC = REPO / "runs" / "original-2026-10-21" / "questions.jsonl"
OUT = HERE / "questions.jsonl"


def main() -> None:
    allq = load_questions(SRC)
    subset = [q for q in allq if q.source.get("work") in WORKS]

    # per-work count oracle
    counts: dict[str, int] = {}
    for q in subset:
        counts[q.source["work"]] = counts.get(q.source["work"], 0) + 1
    for work in WORKS:
        got = counts.get(work, 0)
        if got != EXPECTED_PER_WORK:
            raise SystemExit(f"FAIL: expected {EXPECTED_PER_WORK} questions for {work!r}, got {got}")
    if len(subset) != EXPECTED_PER_WORK * len(WORKS):
        raise SystemExit(f"FAIL: expected {EXPECTED_PER_WORK * len(WORKS)} total, got {len(subset)}")

    write_questions(subset, OUT)

    # fidelity oracle: round-trip must equal the filtered originals exactly
    reloaded = load_questions(OUT)
    if reloaded != subset:
        raise SystemExit("FAIL: reloaded subset != filtered originals (byte/content drift)")

    print(f"OK: wrote {len(subset)} questions to {OUT.relative_to(REPO)}")
    for work in sorted(WORKS):
        print(f"  {counts[work]:3d}  {work}")


if __name__ == "__main__":
    main()
