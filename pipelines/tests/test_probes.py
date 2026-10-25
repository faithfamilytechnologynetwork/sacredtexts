from sacredbench.probes import clustered_accuracy, fold_arabic_letters


def test_letter_fold_maps_alef_and_ta_marbuta():
    folded = fold_arabic_letters("أَة")
    assert "أ" not in folded
    assert "ة" not in folded
    assert "ا" in folded
    assert "ه" in folded


def test_clustered_interval_uses_questions_not_answers():
    rows = []
    for q, outcome in (("q1", "correct"), ("q2", "incorrect")):
        for model in ("a", "b"):
            rows.append({
                "qid": q, "model": model, "outcome": outcome,
                "source": {"work": "W", "version": "V"},
            })
    report = clustered_accuracy(rows, draws=20, seed=1)
    assert report["W · V"]["n_questions"] == 2
    assert report["W · V"]["accuracy"] == 0.5
