"""Issue #96: failure kinds are on the paper's path — `score` reports them in summary.json/summary.md.

Per model × task and per model × text (and their `_overall`): `minor`/`major` beside
correct/incorrect/refused (a split of `incorrect`) and a `kinds` count map that names the near-copy
split (diacritic_only / edition_variant / near_copy). The headline, `outcome` and `scores.jsonl`
are unchanged.
"""

import json
from pathlib import Path

from sacredbench.score import score_file, summary_markdown

REPO_ROOT = Path(__file__).resolve().parents[2]
REF = "the keeper planted twelve trees by the river"


def _row(qid, task, answer, expected):
    return {
        "question_id": qid, "model_id": "m1", "task": task, "answer": answer,
        "question_set_digest": "d",
        "question": {"expected": expected,
                     # romanized Pali keeps its marks (the #94 Latin fold is English-only), so an
                     # accent-only miss stays incorrect and is labeled diacritic_only
                     "source": {"tradition": ["T"], "work": "W", "version": "V", "language": "pi"}},
    }


def _summary(tmp_path):
    rows = [
        _row("rq-0", "retrieve_quote", REF, {"text": REF}),                                  # correct
        _row("rq-1", "retrieve_quote", "the keeper planted twelve tres by the river", {"text": REF}),
        _row("rq-2", "retrieve_quote", "the kéeper planted twelve trées by the river", {"text": REF}),
        _row("rq-3", "retrieve_quote", "an unrelated line about bread and wine", {"text": REF}),
        _row("vs-0", "verify_source", "No.", {"answer": "yes"}),                              # wrong_verdict
        _row("cp-0", "cite_passage", "X 1:1", {"citation": "X 1:1"}),                         # correct
    ]
    answers = tmp_path / "answers.jsonl"
    answers.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
    return score_file(answers, tmp_path / "scores.jsonl")


def test_task_cell_reports_kinds_and_minor_major_beside_incorrect(tmp_path):
    rq = _summary(tmp_path)["models"]["m1"]["retrieve_quote"]
    assert (rq["correct"], rq["incorrect"], rq["refused"]) == (1, 3, 0)
    assert (rq["minor"], rq["major"]) == (2, 1)
    assert rq["kinds"] == {"diacritic_only": 1, "edition_variant": 1, "wrong_passage": 1}
    keys = list(rq)
    assert keys[keys.index("incorrect") + 1: keys.index("incorrect") + 3] == ["minor", "major"]
    assert rq["accuracy"] == 0.25  # headline unchanged: correct/(correct+incorrect)


def test_overall_and_per_text_carry_the_same_split(tmp_path):
    s = _summary(tmp_path)
    ov = s["models"]["m1"]["_overall"]
    assert (ov["incorrect"], ov["minor"], ov["major"]) == (4, 2, 2)
    assert ov["kinds"] == {"diacritic_only": 1, "edition_variant": 1, "wrong_passage": 1, "wrong_verdict": 1}
    text = s["by_text"]["m1"]["W\u0000V\u0000pi"]
    assert text["retrieve_quote"]["kinds"] == {"diacritic_only": 1, "edition_variant": 1, "wrong_passage": 1}
    assert (text["_overall"]["minor"], text["_overall"]["major"]) == (2, 2)
    assert "minor" not in s["by_tradition"]["m1"]["T"]["retrieve_quote"]  # tradition table unchanged


def test_scores_jsonl_rows_are_unchanged(tmp_path):
    _summary(tmp_path)
    for line in (tmp_path / "scores.jsonl").read_text(encoding="utf-8").splitlines():
        m = json.loads(line)["metrics"]
        assert "kind" not in m and "kinds" not in m and m["outcome"] in ("correct", "incorrect", "refused")


def test_markdown_names_the_kinds(tmp_path):
    md = summary_markdown(_summary(tmp_path))
    assert "c/i/r 1/3/0; minor/major 2/1" in md
    assert "### Failure kinds (per task)" in md
    assert "| m1 | retrieve_quote | 3 | 2 | 1 | diacritic_only 1, edition_variant 1, wrong_passage 1 |" in md
    assert "| minor | major | kinds |" in md  # per-text columns


def test_minor_plus_major_is_incorrect_on_a_committed_run(tmp_path):
    """Every incorrect cell of a real run has exactly one kind, per task and per text."""
    run = REPO_ROOT / "runs" / "archive" / "tutorial-2026-10-11"
    s = score_file(run / "answers.jsonl", tmp_path / "scores.jsonl")
    cells = [c for tasks in s["models"].values() for c in tasks.values()]
    cells += [c for texts in s["by_text"].values() for tasks in texts.values() for c in tasks.values()]
    assert cells and all(c["minor"] + c["major"] == c["incorrect"] for c in cells)
    assert (tmp_path / "scores.jsonl").read_bytes() == (run / "scores.jsonl").read_bytes()
