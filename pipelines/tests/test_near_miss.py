"""Issue #96: the near-verbatim tier of incorrect text-retrieval cells.

``metrics.near_miss`` is 1 only on an INCORRECT retrieve_quote/complete_unit cell whose answer is the
right text in another edition or orthography (token_f1 >= 0.9, or the base-letter reference is
word-bounded inside the base-letter answer). It is additive: ``correct``/``outcome`` never read it.
Summaries report the count and its share of ``incorrect`` per task and per text.
"""

import json

from sacredbench.score import score_answer, score_file, summary_markdown

VERSE = "the eternal Ashvattha tree has its roots above and branches below"
SPELLED = "the eternal Asvattha tree has its roots above and branches below"  # one word, F1 10/11
DIACRITIC = "Muḥammad is the messenger of God"


def test_one_changed_word_in_a_long_verse_is_a_near_miss():
    m = score_answer("retrieve_quote", SPELLED, {"text": VERSE})
    assert m["outcome"] == "incorrect" and m["correct"] == 0  # headline unchanged
    assert m["token_f1"] >= 0.9 and m["near_miss"] == 1


def test_base_letter_containment_is_a_near_miss_below_the_f1_bar():
    # a dropped Latin accent: strict F1 is 5/6, but the base letters match word for word
    m = score_answer("complete_unit", "Muhammad is the messenger of God", {"text": DIACRITIC})
    assert m["outcome"] == "incorrect" and m["token_f1"] < 0.9
    assert m["near_miss"] == 1


def test_wrong_text_is_not_a_near_miss():
    m = score_answer("retrieve_quote", "a different verse about a river and its fish", {"text": VERSE})
    assert m["outcome"] == "incorrect" and m["near_miss"] == 0


def test_correct_and_refused_cells_carry_zero():
    assert score_answer("retrieve_quote", VERSE, {"text": VERSE})["near_miss"] == 0
    refused = score_answer("retrieve_quote", "I cannot provide the text of that passage.", {"text": VERSE})
    assert refused["outcome"] == "refused" and refused["near_miss"] == 0


def test_field_is_appended_after_outcome_and_only_on_text_retrieval():
    m = score_answer("retrieve_quote", SPELLED, {"text": VERSE})
    assert list(m)[-2:] == ["outcome", "near_miss"]
    assert "near_miss" not in score_answer("cite_passage", "X 1:2", {"citation": "X 1:1"})
    assert "near_miss" not in score_answer("verify_source", "No.", {"answer": "yes"})


def test_summary_reports_near_miss_beside_incorrect_per_task_and_per_text(tmp_path):
    def row(qid, task, answer, expected):
        return {
            "question_id": qid, "model_id": "m1", "task": task, "answer": answer,
            "question_set_digest": "d",
            "question": {"expected": expected,
                         "source": {"tradition": ["T"], "work": "Gita", "version": "V", "language": "en"}},
        }

    rows = [
        row("rq-0", "retrieve_quote", VERSE, {"text": VERSE}),                     # correct
        row("rq-1", "retrieve_quote", SPELLED, {"text": VERSE}),                   # incorrect, near
        row("rq-2", "retrieve_quote", "nothing like the reference", {"text": VERSE}),  # incorrect
        row("cu-0", "complete_unit", "Muhammad is the messenger of God", {"text": DIACRITIC}),  # near
        row("cp-0", "cite_passage", "X 1:2", {"citation": "X 1:1"}),               # incorrect, no tier
    ]
    answers = tmp_path / "answers.jsonl"
    answers.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    summary = score_file(answers, tmp_path / "scores.jsonl")

    rq = summary["models"]["m1"]["retrieve_quote"]
    assert (rq["correct"], rq["incorrect"], rq["near_miss"], rq["near_miss_share"]) == (1, 2, 1, 0.5)
    assert list(rq)[list(rq).index("incorrect") + 1] == "near_miss"  # beside incorrect
    cu = summary["models"]["m1"]["complete_unit"]
    assert (cu["near_miss"], cu["near_miss_share"]) == (1, 1.0)
    assert "near_miss" not in summary["models"]["m1"]["cite_passage"]
    assert "near_miss" not in summary["models"]["m1"]["_overall"]  # headline aggregates unchanged

    text = summary["by_text"]["m1"]["Gita\u0000V\u0000en"]
    assert (text["retrieve_quote"]["near_miss"], text["retrieve_quote"]["near_miss_share"]) == (1, 0.5)
    assert "near_miss" not in text["cite_passage"]

    md = summary_markdown(summary)
    assert "c/i/r 1/2/0; near 1 = 50% of i" in md
    assert "near miss / text-retrieval incorrect" in md
    assert "| 2/3 (67%) |" in md  # per text: 2 near of 3 text-retrieval incorrect


def test_no_incorrect_means_no_share(tmp_path):
    rows = [{
        "question_id": "rq-0", "model_id": "m1", "task": "retrieve_quote", "answer": VERSE,
        "question_set_digest": "d", "question": {"expected": {"text": VERSE}, "source": {}},
    }]
    answers = tmp_path / "answers.jsonl"
    answers.write_text(json.dumps(rows[0]) + "\n", encoding="utf-8")
    rq = score_file(answers, tmp_path / "scores.jsonl")["models"]["m1"]["retrieve_quote"]
    assert rq["near_miss"] == 0 and rq["near_miss_share"] is None
