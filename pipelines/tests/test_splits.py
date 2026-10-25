from sacredbench.splits import (
    citation_distance,
    fisher_exact,
    format_splits,
    near_copy_by_language,
    other_script_uncertainty,
    quran_bukhari_gap,
    split_run,
)


def test_fisher_matches_the_completion_and_quotation_table():
    # Qur'an 12 correct and 19 incorrect, Bukhari 3 correct and 22 incorrect.
    probability = fisher_exact(12, 19, 3, 22)
    assert 0.03 < probability < 0.04


def test_fisher_is_one_when_both_sides_are_all_incorrect():
    assert fisher_exact(0, 3, 0, 4) == 1.0


def test_gap_skips_refusals_and_the_citation_task():
    rows = [
        _row("quran", "retrieve_quote", "correct", "m"),
        _row("quran", "cite_passage", "incorrect", "m"),
        _row("quran", "complete_unit", "refused", "m"),
        _row("bukhari", "retrieve_quote", "incorrect", "m"),
    ]
    tests = {item["label"]: item for item in quran_bukhari_gap(rows)["tests"]}
    both = tests["both"]
    assert both["quran_correct"] == 1
    assert both["quran_incorrect"] == 0
    assert both["bukhari_incorrect"] == 1
    assert "cite_passage" not in tests  # the gap test skips the citation task entirely


def test_near_copy_is_counted_by_language():
    rows = [{
        "outcome": "incorrect",
        "task": "retrieve_quote",
        "answer": "the same words here",
        "expected": {"text": "the same words here"},
        "metrics": {
            "token_f1": 0.93,
            "normalized": 0,
            "contains_reference": 0,
            "n_candidates": None,
        },
        "source": {"language": "ar"},
    }]
    assert near_copy_by_language(rows)["ar"] == 1


def test_uncertain_other_script_is_counted_without_rescoring():
    rows = [{
        "outcome": "incorrect",
        "task": "complete_unit",
        "answer": "I'm not certain of the rest.",
        "expected": {"text": "وَعَلَّقَتْ"},
        "metrics": {"token_f1": 0.0, "normalized": 0, "contains_reference": 0, "n_candidates": None},
        "source": {"language": "ar"},
    }]
    report = other_script_uncertainty(rows)
    assert report["other_script"] == 1
    assert report["uncertain"] == 1


def test_citation_distance_marks_another_book():
    rows = [{
        "task": "cite_passage",
        "outcome": "incorrect",
        "answer": "2 Kings 10:8",
        "metrics": {"n_candidates": 1},
        "source": {"work": "The Bible", "citation": "2 Chronicles 13:4"},
    }]
    bible = {("2 kings", 10, 8), ("2 chronicles", 13, 4)}
    counts = citation_distance(rows, set(), bible)
    assert counts[("The Bible", "other book")] == 1


def test_format_splits_handles_a_model_that_refused_everything(tmp_path):
    # A model that refused every item has graded=0 -> accuracy None. format_splits must print
    # "—", not crash on a None passed to a float format (the "accuracy if refusals count as
    # incorrect" row).
    import json

    (tmp_path / "answers.jsonl").write_text(
        json.dumps({
            "question_id": "q1", "model_id": "m/all-refused", "answer": "I cannot help with that",
            "question": {"expected": {}, "source": {"work": "W", "version": "V", "language": "en"}},
        }) + "\n"
    )
    (tmp_path / "scores.jsonl").write_text(
        json.dumps({
            "question_id": "q1", "model_id": "m/all-refused", "task": "retrieve_quote",
            "metrics": {"outcome": "refused", "correct": 0},
        }) + "\n"
    )
    report = split_run(tmp_path)
    assert report["sensitivity"]["models"][0]["accuracy"] is None
    out = format_splits(report)  # must not raise on the None accuracy
    # graded accuracy is "—"; counting the refusal as incorrect gives 0/1 = 0.000.
    assert "all-refused: — -> 0.000" in out


def _row(pool: str, task: str, outcome: str, model: str) -> dict:
    if pool == "quran":
        source = {"work": "The Qur'an", "version": "Uthmani", "language": "ar"}
    else:
        source = {"work": "Sahih al-Bukhari", "version": "Arabic", "language": "ar"}
    return {
        "task": task,
        "model": model,
        "outcome": outcome,
        "source": source,
        "answer": "",
        "expected": {},
        "metrics": {},
    }
