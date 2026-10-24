from sacredbench.failure_kind import classify_failure, severity


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
