import json
from collections import Counter
from pathlib import Path

import pytest

from sacredbench.failure_kind import analysis_markdown, breakdown_run, classify_failure, rates, severity

# The shared parity fixture: the SAME cases the viewer's vitest suite asserts against
# (apps/viewer/src/lib/failureKind.test.ts), so classify_failure/classifyFailure AND
# severity/failureSeverity cannot drift.
FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "failure_kind_cases.json"
_CASES = json.loads(FIXTURE.read_text(encoding="utf-8"))["cases"]
_FIELDS = ("name", "expected_kind", "expected_severity")


@pytest.mark.parametrize("case", _CASES, ids=[c["name"] for c in _CASES])
def test_shared_fixture_parity(case):
    """Each shared case classifies to its ``expected_kind`` and ``expected_severity``."""
    kwargs = {k: v for k, v in case.items() if k not in _FIELDS}
    kind = classify_failure(**kwargs)
    assert kind == case["expected_kind"]
    assert severity(kind) == case["expected_severity"]


def test_breakdown_counts_a_shared_text_under_each_listed_tradition(tmp_path):
    # tradition is a LIST and a shared text is counted once per listed tradition (like score.py):
    # a doc with two traditions must appear in BOTH by_tradition rows and BOTH tradition×type rows,
    # while by_document_type and by_task count it only once.
    (tmp_path / "answers.jsonl").write_text(json.dumps({
        "question_id": "q1", "model_id": "m", "answer": "the verse",
        "question": {
            "expected": {"text": "the verse"},
            "source": {
                "document_type": "scripture", "work": "W", "version": "V", "language": "en",
                "tradition": ["Roman Catholic", "Greek Orthodox"],
            },
        },
    }) + "\n")
    (tmp_path / "scores.jsonl").write_text(json.dumps({
        "question_id": "q1", "model_id": "m", "task": "retrieve_quote",
        "metrics": {"outcome": "correct", "correct": 1},
    }) + "\n")

    groups = breakdown_run(tmp_path)
    assert groups["tradition"]["Roman Catholic"]["correct"] == 1
    assert groups["tradition"]["Greek Orthodox"]["correct"] == 1
    assert groups["tradition_and_type"]["Roman Catholic · scripture"]["correct"] == 1
    assert groups["tradition_and_type"]["Greek Orthodox · scripture"]["correct"] == 1
    # counted once, not once per tradition, for document type and task
    assert groups["document_type"]["scripture"]["correct"] == 1
    assert groups["task"]["retrieve_quote"]["correct"] == 1


def test_analysis_markdown_names_outcomes_and_leaves_refusal_unlabeled(tmp_path):
    (tmp_path / "answers.jsonl").write_text(json.dumps({
        "question_id": "q1", "model_id": "m", "answer": "I cannot provide that",
        "question": {
            "expected": {"text": "the reference verse text itself"},
            "source": {
                "document_type": "scripture", "work": "W", "version": "V", "language": "en",
                "tradition": ["Christianity"],
            },
        },
    }) + "\n")
    (tmp_path / "scores.jsonl").write_text(json.dumps({
        "question_id": "q1", "model_id": "m", "task": "retrieve_quote",
        "metrics": {"outcome": "refused", "correct": 0},
    }) + "\n")
    text = analysis_markdown(tmp_path)
    assert "refused=1" in text
    assert "Severity: none." in text
    assert "minor" in text and "major" in text


def test_refused_and_exact_correct_are_unlabeled():
    assert classify_failure(
        task="retrieve_quote", correct=False, refused=True, answer="I can't",
        expected="the reference verse text itself", token_f1=0, normalized=0,
        contains_reference=0, n_candidates=None,
    ) is None
    assert classify_failure(
        task="retrieve_quote", correct=True, refused=False, answer="same",
        expected="same", token_f1=1, normalized=1, contains_reference=1, n_candidates=None,
    ) is None


def test_text_retrieval_kinds():
    assert classify_failure(
        task="retrieve_quote", correct=False, refused=False,
        answer="a completely different sentence here",
        expected="the reference verse text itself",
        token_f1=0.62, normalized=0, contains_reference=0, n_candidates=None,
    ) == "paraphrase"
    assert classify_failure(
        task="retrieve_quote", correct=False, refused=False,
        answer="a completely different sentence here",
        expected="the reference verse text itself",
        token_f1=0.93, normalized=0, contains_reference=0, n_candidates=None,
    ) == "near_copy"
    assert classify_failure(
        task="complete_unit", correct=False, refused=False,
        answer="a completely different sentence here",
        expected="the reference verse text itself",
        token_f1=0.1, normalized=0, contains_reference=0, n_candidates=None,
    ) == "wrong_passage"
    assert classify_failure(
        task="retrieve_quote", correct=False, refused=False,
        answer="the reference",
        expected="the reference verse text itself and more words",
        token_f1=0.5, normalized=0, contains_reference=0, n_candidates=None,
    ) == "omission"
    assert classify_failure(
        task="retrieve_quote", correct=False, refused=False,
        answer="In the beginning God created the heaven",
        expected="בְּרֵאשִׁית בָּרָא אֱלֹהִים",
        token_f1=0, normalized=0, contains_reference=0, n_candidates=None,
    ) == "other_script"


def test_addition_does_not_require_incorrect():
    expected = "one two three four"
    answer = expected + " five six seven eight nine ten eleven twelve"
    assert classify_failure(
        task="retrieve_quote", correct=True, refused=False, answer=answer, expected=expected,
        token_f1=0.5, normalized=0, contains_reference=1, n_candidates=None,
    ) == "addition"


def test_severity_separates_a_miss_on_the_passage_from_a_replaced_object():
    assert severity("paraphrase") == "minor"
    assert severity("omission") == "minor"
    assert severity("addition") == "minor"
    assert severity("wrong_locus") == "major"
    assert severity("other_script") == "major"
    assert rates(Counter(correct=3, incorrect=1, refused=1)) == (0.75, 0.2)
    assert rates(Counter()) == (None, None)
    assert severity("near_copy") == "minor"
    assert severity(None) is None


def test_citation_and_verdict():
    base = dict(
        correct=False, refused=False, answer="x", expected="y",
        token_f1=None, normalized=None, contains_reference=None,
    )
    assert classify_failure(task="cite_passage", n_candidates=2, **base) == "hedge"
    assert classify_failure(task="cite_passage", n_candidates=1, **base) == "wrong_locus"
    assert classify_failure(task="cite_passage", n_candidates=0, **base) == "no_citation"
    assert classify_failure(task="verify_source", n_candidates=None, **base) == "wrong_verdict"
