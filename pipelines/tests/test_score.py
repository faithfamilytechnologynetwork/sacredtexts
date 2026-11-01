import json
from pathlib import Path

import pytest

from sacredbench.jev import RUBRIC_ID, JevError, answer_digest
from sacredbench.score import (
    ScoreError,
    normalize,
    parse_yes_no,
    score_answer,
    score_file,
    summary_markdown,
    token_f1,
)


def _row(qid, digest, **over):
    r = {
        "question_id": qid, "model_id": "m1", "task": "retrieve_quote",
        "answer": "x", "question": {"expected": {"text": "x"}},
    }
    if digest is not None:
        r["question_set_digest"] = digest
    r.update(over)
    return r


def test_normalize_folds_unicode_and_punct():
    assert normalize("“Love one’s neighbour!”") == normalize('"Love one\'s neighbour"')
    assert normalize("A  B\n C") == "a b c"


def test_token_f1_bounds():
    assert token_f1("the keeper planted trees", "the keeper planted trees") == 1.0
    assert token_f1("entirely different words here", "the keeper planted trees") == 0.0
    assert 0.0 < token_f1("the keeper planted", "the keeper planted trees") < 1.0


@pytest.mark.parametrize("ans,expected", [
    ("Yes.", "yes"), ("no,", "no"), ("NO!", "no"), ("maybe", None),
    # leading verdict wins even with a later incidental token ("no doubt")
    ("Yes, there is no doubt about it.", "yes"),
    # Spec 26 leading-stance (#23 PAPER GATE): the verdict must be the LEADING token
    ("No, that is from Sahih Muslim", "no"),            # leading No
    ('"No" — that is from Sahih Muslim', "no"),         # quoted leading No
    ("**Yes**", "yes"),                                  # markdown-wrapped leading Yes
    ("Answer: Yes", "yes"),                              # bare "Answer:" label stripped (architect)
    ("Verdict - No", "no"),                              # "Verdict -" label stripped
    ("Response: yes, it is.", "yes"),                    # "Response:" label stripped
    ("There is no way to verify this... Yes", None),     # negation-evasion: "no" buried, not leading
    ("Based on my search, yes", None),                   # verdict not leading (no label) -> None
    ("It is not from this edition.", None),              # leads with "It", not a Yes/No verdict
    ("I think yes.", None),                              # not a leading verdict
    ("yesterday it rained", None),                       # "yes" is not a whole-word verdict
])
def test_parse_yes_no(ans, expected):
    # the LEADING-stance Yes/No (Spec 26); a DECLINE is handled by the outcome layer, not here
    assert parse_yes_no(ans) == expected


def test_verify_source_negation_evasion_is_refused_not_correct():
    # the #23 case: a non-declining negation-evasion must NOT score a false-premise "no" correct;
    # with no leading verdict it is REFUSED (parsed is None), excluded from accuracy
    r = score_answer("verify_source", "There is no way to verify this... Yes", {"answer": "no"})
    assert r["parsed"] is None and r["correct"] == 0 and r["outcome"] == "refused"


def test_verify_source_committed_verdict_with_trailing_decline_is_graded():
    # a LEADING verdict counts even when followed by a decline ("No, though I cannot verify…") —
    # refused is parsed-is-None, not a decline-cue scan
    r = score_answer("verify_source", "No, I cannot verify that this is from X.", {"answer": "no"})
    assert r["parsed"] == "no" and r["correct"] == 1 and r["outcome"] == "correct"
    # no leading verdict at all -> refused
    assert score_answer("verify_source", "I cannot determine that.", {"answer": "no"})["outcome"] == "refused"


# --- issue #76: per-script leading-stance yes/no --------------------------------------------------

@pytest.mark.parametrize("ans,lang,expected", [
    # bare native verdicts parse on their own script
    ("نعم", "ar", "yes"), ("لا", "ar", "no"),
    ("كن", "he", None),                                   # not a Hebrew verdict word
    ("כן", "he", "yes"), ("לא", "he", "no"),
    ("ਹਾਂ", "pa", "yes"), ("ਨਹੀਂ", "pa", "no"),
    ("हाँ", "sa", "yes"), ("हां", "sa", "yes"), ("नहीं", "sa", "no"),
    ("āma", "pi", "yes"), ("na", "pi", "no"),
    # leading native verdict wins even with a trailing clause (same as the English leading-stance)
    ("لا، بل هو من صحيح مسلم", "ar", "no"),
    ("כן, זה מספר תהילים", "he", "yes"),
    # English is ALWAYS eligible, whatever the cell language (a model may answer in English)
    ("No", "ar", "no"), ("Yes.", "pi", "yes"),
])
def test_parse_yes_no_native_scripts(ans, lang, expected):
    assert parse_yes_no(ans, lang) == expected


@pytest.mark.parametrize("ans,lang", [
    # #23 hardening per script: the verdict token is NOT leading (a non-verdict word leads, the
    # verdict is buried) -> None (refused), never gamed into a false-premise correct.
    ("أعتقد أنه لا يمكن التحقق من ذلك، لكن نعم", "ar"),     # leads "أعتقد" (I think)
    ("אני חושב שאי אפשר לאמת זאת, אבל כן", "he"),           # leads "אני" (I)
    ("ਮੈਨੂੰ ਲੱਗਦਾ ਹੈ ਕਿ ਪੁਸ਼ਟੀ ਨਹੀਂ ਹੋ ਸਕਦੀ, ਪਰ ਹਾਂ", "pa"),
    ("मुझे लगता है कि इसे सत्यापित नहीं किया जा सकता, लेकिन हाँ", "sa"),
    ("ahaṃ na jānāmi, āma", "pi"),                          # leads "ahaṃ" (I), buried "na"/"āma"
])
def test_parse_yes_no_native_negation_evasion_is_none(ans, lang):
    assert parse_yes_no(ans, lang) is None


@pytest.mark.parametrize("ans,lang", [
    # PR #78 review: a native "no" word is ALSO the sentence-negation particle. A refusal that opens
    # with it ("I cannot verify", "I don't know") must stay refused, never be scored a verdict.
    ("لا أستطيع التحقق من ذلك", "ar"),                      # "I cannot verify that"
    ("لا أعرف", "ar"),                                     # "I don't know"
    ("لا سبيل إلى التحقق من ذلك، لكن نعم", "ar"),           # the parse_yes_no docstring example
    ("لاَ أعرف", "ar"),                                     # a diacritic on the particle changes nothing
    ("לא ניתן לאמת זאת", "he"),                             # "this cannot be verified"
    ("לא יודע", "he"),                                     # "don't know"
    ("na jānāmi", "pi"),                                   # "I do not know"
    ("ਨਹੀਂ ਪਤਾ", "pa"),                                     # "don't know"
    ("नहीं पता", "sa"),                                     # "don't know"
    ("Όχι μόνο αυτό", "grc"),                              # "not only this"
    # a word that merely BEGINS with the native token is not the token
    ("لاحظت أن هذا النص", "ar"), ("natthi", "pi"), ("Ναιάδα", "grc"), ("לאחר עיון, כן", "he"),
    # symmetric rule: a native YES word followed by another word is not read either, so the stand-alone
    # rule cannot bias the parser towards one verdict
    ("نعم هذا من القرآن", "ar"),
])
def test_parse_yes_no_native_negation_particle_is_not_a_verdict(ans, lang):
    assert parse_yes_no(ans, lang) is None


@pytest.mark.parametrize("ans,lang,expected", [
    # PR #78 review: the terminator is read by Unicode category, so a word ending in a nasal/vowel mark
    # (ਹਾਂ, हाँ, नहीं) still ends at a danda (।, U+0964) — `\b` alone misses it
    ("ਹਾਂ।", "pa", "yes"), ("ਨਹੀਂ।", "pa", "no"), ("ਹਾਂ ।", "pa", "yes"),
    ("हाँ।", "sa", "yes"), ("नहीं।", "sa", "no"), ("हां॥", "sa", "yes"),
    # Greek, as the Greek prompt asks (ναι ή όχι) — added in PR #78 round 2
    ("Ναι", "grc", "yes"), ("ναι.", "grc", "yes"), ("Ναί, είναι από το Ευαγγέλιο", "grc", "yes"),
    ("Όχι", "grc", "no"), ("όχι.", "grc", "no"), ("ὄχι, ...", "grc", "no"),
    # a native verdict followed by punctuation or wrapped in quotes still parses
    ("«لا»", "ar", "no"), ("لا،", "ar", "no"), ("لا.", "ar", "no"), ("نعم، هذا من القرآن", "ar", "yes"),
    ("לא.", "he", "no"), ("**כן**", "he", "yes"),
    ("na.", "pi", "no"), ("āma, ...", "pi", "yes"),
])
def test_parse_yes_no_native_verdict_then_punctuation(ans, lang, expected):
    assert parse_yes_no(ans, lang) == expected


@pytest.mark.parametrize("ans,expected", [
    # PR #78 round 2: a vowelled verdict is the same word
    ("نَعَمْ.", "yes"), ("نَعَمْ", "yes"), ("لَا،", "no"), ("لَا", "no"), ("«لَا»", "no"),
    # ... and the native "Answer:" label is stripped like the English one
    ("الجواب: لا", "no"), ("الجواب: نعم.", "yes"), ("الإجابة: نعم", "yes"), ("الاجابة - لا", "no"),
    ("الرد: لا", "no"), ("الجَوَابُ: نَعَمْ", "yes"), ("**الجواب:** لا", "no"), ("Answer: لا", "no"),
    # the stand-alone rule still applies after a vowelled particle or a label
    ("لَا أَعْرِفُ", None), ("الجواب: لا أستطيع التحقق", None), ("الجواب: لا يمكن الجزم", None),
    # a label is only a label with its colon/dash; a buried verdict is not leading
    ("الجواب لا", None), ("الجواب هو: نعم", None),
])
def test_parse_yes_no_arabic_vowels_and_label(ans, expected):
    assert parse_yes_no(ans, "ar") == expected


def test_native_label_and_marks_do_not_touch_other_cells():
    # the Arabic label is read only on an Arabic cell; English parsing is byte-identical
    assert parse_yes_no("الجواب: لا", "he") is None
    assert parse_yes_no("الجواب: لا", None) is None
    assert parse_yes_no("Answer: no") == parse_yes_no("Answer: no", "ar") == "no"


def test_native_tokens_only_eligible_for_their_language():
    # A native token is NOT read when the cell language does not select it. This is what keeps every
    # committed (English-answer) verify cell byte-stable: adding native tables cannot flip a cell whose
    # language does not carry those tokens. The Latin Pali "na" is the sharp case.
    assert parse_yes_no("لا", None) is None            # Arabic "no" with no language -> not read
    assert parse_yes_no("لا", "he") is None            # wrong script's table -> not read
    assert parse_yes_no("na", None) is None            # Pali "no" is never read as English
    assert parse_yes_no("na", "ar") is None            # ... nor on a non-Pali cell
    assert parse_yes_no("na", "pi") == "no"            # only on a Pali cell
    # English behaviour is unchanged whether or not a language is passed
    assert parse_yes_no("Yes.") == parse_yes_no("Yes.", "ar") == "yes"


def test_score_answer_plumbs_language_for_native_verdict():
    # score_answer forwards the question language so a native verdict is graded, not refused.
    graded = score_answer("verify_source", "لا، هذا من صحيح مسلم", {"answer": "no"}, language="ar")
    assert graded["parsed"] == "no" and graded["correct"] == 1 and graded["outcome"] == "correct"
    # without the language the same answer has no readable leading verdict -> refused (old behaviour)
    assert score_answer("verify_source", "لا، هذا من صحيح مسلم", {"answer": "no"})["outcome"] == "refused"


def test_retrieve_quote_tiers():
    exp = {"text": "The keeper planted twelve trees."}
    exact = score_answer("retrieve_quote", "The keeper planted twelve trees.", exp)
    assert exact == {
        "exact": 1, "normalized": 1, "token_f1": 1.0, "token_f1_base": 1.0, "contains_reference": 1,
        "correct": 1, "outcome": "correct",
    }
    punct = score_answer("retrieve_quote", "the keeper planted twelve trees", exp)
    assert (punct["exact"], punct["normalized"], punct["correct"]) == (0, 1, 1)
    wrong = score_answer("retrieve_quote", "something else entirely different", exp)
    assert wrong["correct"] == 0 and wrong["token_f1"] == 0.0 and wrong["outcome"] == "incorrect"


def test_default_graders_dict_shape_and_noop():
    # the default grader set emits the phase-1 submetric block (keys, order, values) PLUS the
    # phase-3 `outcome` field appended last. The grader selection itself is a no-op (implicit default
    # == explicit default); the run byte-guards prove the full dict over 800 real cells.
    exp = {"text": "The keeper planted twelve trees."}
    ans = "﴾The keeper planted twelve trees.﴿ (from a web page)"
    import json
    from sacredbench.graders import resolve_evaluators
    default_implicit = score_answer("retrieve_quote", ans, exp)
    default_explicit = score_answer("retrieve_quote", ans, exp, resolve_evaluators(None))
    assert json.dumps(default_implicit) == json.dumps(default_explicit)
    assert list(default_implicit) == [
        "exact", "normalized", "token_f1", "token_f1_base", "contains_reference", "correct", "outcome",
    ]


def test_contains_reference_wrapped_exact_flips_headline():
    # Spec 15: a verbatim quote wrapped in brackets + an English caveat scores normalized=0
    # (it is NOT "the quote and nothing else") but contains_reference=1 → correct=1.
    exp = {"text": "The keeper planted twelve trees."}
    wrapped = score_answer(
        "retrieve_quote",
        "﴾The keeper planted twelve trees.﴿\n\n(Note: retrieved from a web page.)",
        exp,
    )
    assert wrapped["normalized"] == 0
    assert wrapped["contains_reference"] == 1
    assert wrapped["correct"] == 1
    # complete_unit carries the signal too (symmetry)
    assert "contains_reference" in score_answer("complete_unit", "x", {"text": "x"})


def test_greek_accents_are_not_word_breaks():
    """A Greek accent must not split the word. An unaccented answer still matches."""
    assert normalize("λόγος") == normalize("λογος")
    assert " " not in normalize("λόγος")
    # A Latin accent stays on the letter. It is not stripped, and it is not a break.
    assert normalize("café") == "café"
    assert " " not in normalize("café")
    path = Path(__file__).resolve().parents[2] / "items/for-test/christianity/native/greek/population/prompt-native/questions.jsonl"
    row = next(json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if json.loads(line)["task"] == "complete_unit")
    text = row["expected"]["text"]
    assert score_answer("complete_unit", text, row["expected"])["correct"] == 1
    assert score_answer("complete_unit", normalize(text), row["expected"])["normalized"] == 1
    assert score_answer("complete_unit", text + " καὶ τὰ ἑξῆς", row["expected"])["correct"] == 1


def test_complete_unit_allows_verses_after_the_remainder():
    """Continuing into later verses still contains the scored remainder, so it is correct.

    The headline is normalized OR containment. Extra words after the remainder fail
    normalized equality and pass containment. A different remainder does not.
    """
    remainder = "the remaining words of this verse"
    continued = score_answer(
        "complete_unit",
        remainder + " And the next verse goes on for several more lines.",
        {"text": remainder, "full_text": "head " + remainder},
    )
    assert continued["normalized"] == 0
    assert continued["contains_reference"] == 1
    assert continued["correct"] == 1
    wrong = score_answer("complete_unit", "some other verse entirely", {"text": remainder})
    assert wrong["correct"] == 0


def test_contains_reference_is_superset_and_bounded():
    exp = {"text": "The keeper planted twelve trees."}
    # a strict match is contained
    assert score_answer("retrieve_quote", "The keeper planted twelve trees.", exp)["contains_reference"] == 1
    # near-miss that does NOT contain the reference is not rescued
    near = score_answer("retrieve_quote", "The keeper planted twelve oaks.", exp)
    assert near["contains_reference"] == 0 and near["correct"] == 0
    # word boundary: the shorter reference must not match inside a longer token
    assert score_answer("retrieve_quote", "Jude 1:30", {"text": "Jude 1:3"})["contains_reference"] == 0


def test_contains_reference_empty_reference_guard():
    # an empty-normalising reference must not match everywhere (re.escape("") matches anywhere)
    r = score_answer("retrieve_quote", "literally anything", {"text": "   "})
    assert r["contains_reference"] == 0 and r["correct"] == 0


def test_contains_reference_scoped_to_text_retrieval_only():
    # the provenance tasks must NEVER carry a contains_reference key
    assert "contains_reference" not in score_answer("verify_source", "Yes", {"answer": "yes"})
    assert "contains_reference" not in score_answer("cite_passage", "Jude 1:3", {"citation": "Jude 1:3"})


def test_retired_tasks_are_unknown():
    # identify_version / identify_source are retired in Spec 26
    for task in ("identify_version", "identify_source"):
        with pytest.raises(ScoreError, match="unknown task"):
            score_answer(task, "x", {})


# --- outcome classification (Spec 15 phase 3) --------------------------------


def test_refusal_short_circuits_headline_but_keeps_submetrics():
    # a leading decline that does NOT contain the reference -> refused, correct forced to 0, but the
    # exact/normalized/token_f1/contains_reference submetrics are preserved (the oracle depends on it)
    exp = {"text": "The keeper planted twelve trees."}
    r = score_answer("retrieve_quote", "I can't reliably reproduce that verse from memory.", exp)
    assert r["outcome"] == "refused" and r["correct"] == 0
    for k in ("exact", "normalized", "token_f1", "contains_reference"):
        assert k in r
    assert r["contains_reference"] == 0  # not contained


def test_decline_prefixed_but_delivers_is_not_refused():
    # the matcher's containment half: a decline-prefixed answer that still DELIVERS the verse is an
    # answer, not a refusal (mirrors the real opus-search Ketubot 8a:8 cell, retrieve_quote-4ad4392645da)
    exp = {"text": "The keeper planted twelve trees."}
    delivered = score_answer(
        "retrieve_quote",
        "I couldn't fully confirm this, but it is: The keeper planted twelve trees.",
        exp,
    )
    assert delivered["contains_reference"] == 1
    assert delivered["outcome"] == "correct" and delivered["correct"] == 1


def test_wrapped_and_near_miss_are_not_refused():
    exp = {"text": "The keeper planted twelve trees."}
    wrapped = score_answer("retrieve_quote", "﴾The keeper planted twelve trees.﴿ (web)", exp)
    assert wrapped["outcome"] == "correct"  # delivered, no decline
    near = score_answer("retrieve_quote", "The keeper planted twelve oaks.", exp)
    assert near["outcome"] == "incorrect"  # a wrong attempt, not a refusal


def test_verify_source_decline_is_refused():
    # a leading decline on verify_source is a refusal regardless of any incidental Yes/No token it
    # contains — otherwise an explicit decline could score correct via the first-token parser
    r = score_answer("verify_source", "I can't verify that claim.", {"answer": "yes"})
    assert r["outcome"] == "refused" and r["correct"] == 0
    # a committed Yes/No (no leading decline) is graded normally even if wrong
    assert score_answer("verify_source", "No.", {"answer": "yes"})["outcome"] == "incorrect"
    # declines whose incidental token happens to MATCH the expected answer must NOT score correct
    for ans, exp in [
        ("I can't verify whether the answer is yes.", "yes"),           # single incidental "yes"
        ("I cannot verify this; no reliable source is available.", "no"),  # single incidental "no"
        ("I can't verify whether the answer is yes or no.", "yes"),      # both tokens
    ]:
        c = score_answer("verify_source", ans, {"answer": exp})
        assert c["outcome"] == "refused" and c["correct"] == 0, ans
    # a genuine leading "Yes" verdict with a later incidental "no" stays a committed, correct answer
    ok = score_answer("verify_source", "Yes, there is no doubt that this is from John 1:1.", {"answer": "yes"})
    assert ok["outcome"] == "correct" and ok["correct"] == 1


def test_hedged_but_correct_provenance_is_not_refused():
    # the provenance guard (_with_outcome gates refusal on `not correct`): a leading decline that
    # STILL delivers the correct answer stays correct — provenance tasks have no containment half in
    # classify_refusal, so without the gate a hedged-but-correct citation would be wrongly refused.
    cite = score_answer("cite_passage", "I can't be fully certain, but it is Jude 1:3.", {"citation": "Jude 1:3"})
    assert cite["correct"] == 1 and cite["outcome"] == "correct"
    # verify_source: a LEADING verdict counts even with a trailing hedge (Spec 26 leading-stance —
    # a buried verdict after a decline no longer counts; see test_parse_yes_no)
    yes = score_answer("verify_source", "Yes, though I can't be fully certain.", {"answer": "yes"})
    assert yes["correct"] == 1 and yes["outcome"] == "correct"
    # a declined provenance answer that does NOT deliver is still refused
    assert score_answer("cite_passage", "I can't provide the citation.", {"citation": "Jude 1:3"})["outcome"] == "refused"


def test_summary_accuracy_excludes_refused_with_coverage(tmp_path):
    answers = tmp_path / "answers.jsonl"
    exp = {"text": "alpha beta gamma"}
    rows = [
        _answer("retrieve_quote-0", "m1", "retrieve_quote", "alpha beta gamma", exp, ["A"]),         # correct
        _answer("retrieve_quote-1", "m1", "retrieve_quote", "delta epsilon zeta", exp, ["A"]),       # incorrect
        _answer("retrieve_quote-2", "m1", "retrieve_quote", "I can't reliably reproduce it.", exp, ["A"]),  # refused
        _answer("retrieve_quote-3", "m1", "retrieve_quote", "I don't have access to that text.", exp, ["A"]),  # refused
    ]
    answers.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    cell = score_file(answers, tmp_path / "scores.jsonl")["models"]["m1"]["retrieve_quote"]
    assert cell["n"] == 4 and cell["correct"] == 1 and cell["incorrect"] == 1 and cell["refused"] == 2
    assert cell["accuracy"] == 0.5    # 1 correct / 2 graded (refusals excluded)
    assert cell["coverage"] == 0.5    # 2 graded / 4 answered
    assert cell["refused_rate"] == 0.5
    # submetric average is over graded cells only (2), not n (4)
    assert cell["contains_reference"] == 0.5
    # the three-outcome counts are rendered in summary.md too (spec: summary.json AND summary.md)
    md = summary_markdown(score_file(answers, tmp_path / "s3.jsonl"))
    assert "c/i/r 1/1/2" in md and "refused_rate" in md


def test_all_refused_accuracy_is_null(tmp_path):
    answers = tmp_path / "answers.jsonl"
    exp = {"text": "alpha beta gamma"}
    rows = [
        _answer("retrieve_quote-0", "m1", "retrieve_quote", "I can't reliably reproduce it.", exp, ["A"]),
        _answer("retrieve_quote-1", "m1", "retrieve_quote", "I don't have that text.", exp, ["A"]),
    ]
    answers.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    cell = score_file(answers, tmp_path / "scores.jsonl")["models"]["m1"]["retrieve_quote"]
    assert cell["refused"] == 2 and cell["accuracy"] is None and cell["coverage"] == 0.0
    assert cell["contains_reference"] is None  # no graded cells -> no diagnostic average
    assert "n/a" in summary_markdown(score_file(answers, tmp_path / "s2.jsonl"))


def test_summary_stamps_evaluators(tmp_path):
    answers = tmp_path / "answers.jsonl"
    answers.write_text(json.dumps(_answer("retrieve_quote-0", "m1", "retrieve_quote", "x", {"text": "x"}, ["A"])) + "\n")
    summary = score_file(answers, tmp_path / "scores.jsonl")
    assert summary["evaluators"] == ["strict", "containment"]  # default set, provenance-stamped


# ---- `score --judgments` provenance opt-in (Spec 21 phase 2) --------------

def _answers_file(tmp_path, digest="d"):
    answers = tmp_path / "answers.jsonl"
    answers.write_text(
        json.dumps(_answer("retrieve_quote-0", "m1", "retrieve_quote", "x", {"text": "x"}, ["A"], digest=digest)) + "\n"
    )
    return answers


def _sidecar_with_manifest(tmp_path, *, resolved="typesafe/jev-1.14-20261014", digest="d",
                           rubric=RUBRIC_ID, rows=True, adigest=None):
    """A judgments sidecar + sibling manifest. `rows=True` writes one real verdict row that agrees
    with the manifest (build + question-set digest) AND with _answers_file's answer "x" (its
    answer_digest), so `score --judgments` binds; pass `adigest` to force a non-matching answer.
    `rows=False` leaves the sidecar empty."""
    sidecar = tmp_path / "judgments.jsonl"
    if rows:
        row = {
            "question_id": "retrieve_quote-0", "model_id": "m1", "model": "jev",
            "rubric_id": RUBRIC_ID, "judge_model": "jev-latest", "judge_model_resolved": resolved,
            "question_set_digest": digest,
            "answer_digest": adigest if adigest is not None else answer_digest("x"),
            "refusal_p": 0.1, "matches_requested_p": 0.9, "equivalence": "not_evaluated",
            "usage": {"in": 1, "out": 1, "cost": 1e-5},
        }
        sidecar.write_text(json.dumps(row) + "\n")
    else:
        sidecar.write_text("")
    (tmp_path / "judgments.jsonl.manifest.json").write_text(json.dumps({
        "rubric_id": rubric, "judge_model": "jev-latest", "judge_model_resolved": resolved,
        "question_set_digest": digest, "index_digest": None,
    }))
    return sidecar


def test_default_score_has_no_judge_key(tmp_path):
    # Without --judgments, `score` is unchanged: no `judge` provenance key enters the summary.
    summary = score_file(_answers_file(tmp_path), tmp_path / "scores.jsonl")
    assert "judge" not in summary


def test_judgments_stamps_resolved_build_in_sibling_key(tmp_path):
    sidecar = _sidecar_with_manifest(tmp_path)
    summary = score_file(_answers_file(tmp_path), tmp_path / "scores.jsonl", judgments=sidecar)
    assert summary["judge"] == {"model_resolved": "typesafe/jev-1.14-20261014", "rubric_id": RUBRIC_ID}
    # evaluators stays a name list; the judge key adds no cost/usage field to the SUMMARY (the sidecar
    # row's own usage.cost never reaches it) — mirrors the test_tutorial_run.py:66 guard.
    assert summary["evaluators"] == ["strict", "containment"]
    assert "cost" not in json.dumps(summary).lower()


def test_judgments_from_different_answers_rejected(tmp_path):
    # architect PR#47 #2: a sidecar whose rows are for DIFFERENT answers (same question set) must not
    # stamp provenance. The row's answer_digest does not match _answers_file's answer "x".
    sidecar = _sidecar_with_manifest(tmp_path, adigest=answer_digest("a completely different answer"))
    with pytest.raises(JevError, match="does not match any answer being scored"):
        score_file(_answers_file(tmp_path), tmp_path / "scores.jsonl", judgments=sidecar)


def test_judgments_empty_sidecar_fails_fast(tmp_path):
    # A manifest alone is not proof of verdicts: an empty sidecar must NOT stamp a judge build
    # (codex phase-2 finding — provenance would otherwise claim a pass that produced nothing).
    sidecar = _sidecar_with_manifest(tmp_path, rows=False)
    with pytest.raises(JevError, match="no judgments recorded"):
        score_file(_answers_file(tmp_path), tmp_path / "scores.jsonl", judgments=sidecar)


def test_judgments_skeletal_row_fails_fast(tmp_path):
    # codex iter-2: a row carrying ONLY rubric/build/qsd (no question_id/verdict fields) keys as
    # present but is not a judgment — provenance must not be stamped for it.
    sidecar = tmp_path / "judgments.jsonl"
    sidecar.write_text(json.dumps({
        "rubric_id": RUBRIC_ID, "judge_model_resolved": "typesafe/jev-1.14-20261014",
        "question_set_digest": "d",
    }) + "\n")
    (tmp_path / "judgments.jsonl.manifest.json").write_text(json.dumps({
        "rubric_id": RUBRIC_ID, "judge_model": "jev-latest",
        "judge_model_resolved": "typesafe/jev-1.14-20261014", "question_set_digest": "d",
        "index_digest": None,
    }))
    with pytest.raises(JevError, match="not a complete judgment"):
        score_file(_answers_file(tmp_path), tmp_path / "scores.jsonl", judgments=sidecar)


def test_judgments_row_missing_verdict_fields_fails_fast(tmp_path):
    # a row with full identity but no refusal_p/matches_requested_p is still not a judgment
    sidecar = tmp_path / "judgments.jsonl"
    sidecar.write_text(json.dumps({
        "question_id": "retrieve_quote-0", "model_id": "m1", "answer_digest": "a0",
        "rubric_id": RUBRIC_ID, "judge_model_resolved": "typesafe/jev-1.14-20261014",
        "question_set_digest": "d",
    }) + "\n")
    (tmp_path / "judgments.jsonl.manifest.json").write_text(json.dumps({
        "rubric_id": RUBRIC_ID, "judge_model": "jev-latest",
        "judge_model_resolved": "typesafe/jev-1.14-20261014", "question_set_digest": "d",
        "index_digest": None,
    }))
    with pytest.raises(JevError, match="refusal_p"):
        score_file(_answers_file(tmp_path), tmp_path / "scores.jsonl", judgments=sidecar)


def test_judgments_row_build_mismatch_fails_fast(tmp_path):
    # a row whose resolved build disagrees with the manifest is refused (mixed-build sidecar)
    sidecar = _sidecar_with_manifest(tmp_path)
    rogue = {"question_id": "retrieve_quote-1", "model_id": "m1", "rubric_id": RUBRIC_ID,
             "judge_model_resolved": "typesafe/jev-9.9-OTHER", "question_set_digest": "d",
             "answer_digest": "a1"}
    with sidecar.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rogue) + "\n")
    with pytest.raises(JevError, match="no mixed-build files"):
        score_file(_answers_file(tmp_path), tmp_path / "scores.jsonl", judgments=sidecar)


def test_judgments_wrong_question_set_fails_fast(tmp_path):
    # the sidecar manifest's digest must bind to the answers being scored
    sidecar = _sidecar_with_manifest(tmp_path, digest="other-set")
    with pytest.raises(JevError, match="different question set"):
        score_file(_answers_file(tmp_path, digest="d"), tmp_path / "scores.jsonl", judgments=sidecar)


def test_judgments_missing_manifest_fails_fast(tmp_path):
    bare = tmp_path / "bare.jsonl"
    bare.write_text("")  # no sibling .manifest.json
    with pytest.raises(JevError, match="no manifest"):
        score_file(_answers_file(tmp_path), tmp_path / "scores.jsonl", judgments=bare)


def test_judgments_wrong_rubric_fails_fast(tmp_path):
    sidecar = _sidecar_with_manifest(tmp_path, rubric="not-the-rubric")
    with pytest.raises(JevError, match="rubric"):
        score_file(_answers_file(tmp_path), tmp_path / "scores.jsonl", judgments=sidecar)


def test_verify_and_citation_tasks():
    assert score_answer("verify_source", "No, it is not.", {"answer": "no", "true_work": "X"})["correct"] == 1
    assert score_answer("cite_passage", "That is Jude 1:3.", {"citation": "Jude 1:3"})["correct"] == 1
    assert score_answer("cite_passage", "That is Jude 1:4.", {"citation": "Jude 1:3"})["correct"] == 0


def test_score_file_and_summary(tmp_path):
    answers = tmp_path / "answers.jsonl"
    rows = [
        {
            "question_id": "retrieve_quote-00000", "model_id": "m1", "task": "retrieve_quote",
            "answer": "alpha beta gamma", "question_set_digest": "deadbeef",
            "question": {"expected": {"text": "alpha beta gamma"}},
        },
        {
            "question_id": "verify_source-00001", "model_id": "m1", "task": "verify_source",
            "answer": "Yes", "question_set_digest": "deadbeef",
            "question": {"expected": {"answer": "no", "true_work": "W"}},
        },
    ]
    answers.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    summary = score_file(answers, tmp_path / "scores.jsonl")
    m1 = summary["models"]["m1"]
    assert m1["retrieve_quote"]["accuracy"] == 1.0
    assert m1["verify_source"]["accuracy"] == 0.0
    assert m1["_overall"]["n"] == 2 and m1["_overall"]["accuracy"] == 0.5
    md = summary_markdown(summary)
    assert "m1" in md and "retrieve_quote" in md
    # no run config → usage is still emitted (evidence-derived) but no panel "proof"
    assert "usage" in summary and "panel" not in summary
    assert "Panel" not in md


def test_usage_totals_and_partial_pricing(tmp_path):
    answers = tmp_path / "answers.jsonl"
    rows = [
        _row("retrieve_quote-0", "deadbeef", model_id="a", model="m-a",
             usage={"in": 1000, "out": 2000, "provider": "HostX"}),
        _row("retrieve_quote-1", "deadbeef", model_id="b", model="m-b",
             usage={"in": 500, "out": 500}),  # no serving-host field
    ]
    answers.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    # prices only for model 'a' → 'a' gets a cost, 'b' does not, and NO total cost is
    # emitted (a subtotal over part of the panel must not masquerade as the total)
    panel = {"a": {"provider": "openai", "model": "m-a", "endpoint": "h", "price_in": 1.0, "price_out": 2.0}}
    summary = score_file(answers, tmp_path / "scores.jsonl", panel=panel)
    u = summary["usage"]
    assert u["per_model"]["a"]["cost_usd"] == 1000/1e6*1.0 + 2000/1e6*2.0
    assert "cost_usd" not in u["per_model"]["b"]
    assert u["total"]["in"] == 1500 and u["total"]["out"] == 2500 and u["total"]["calls"] == 2
    assert "cost_usd" not in u["total"]  # partial pricing → no total cost
    md = summary_markdown(summary)
    assert "n/a (partial pricing)" in md  # unpriced total rendered honestly
    # panel: provider proof from config, serving host from the answers' usage
    assert summary["panel"]["a"]["provider"] == "openai"
    assert summary["panel"]["a"]["served_by"] == ["HostX"]


def test_total_cost_when_every_model_priced(tmp_path):
    answers = tmp_path / "answers.jsonl"
    rows = [
        _row("retrieve_quote-0", "deadbeef", model_id="a", model="m-a", usage={"in": 1000, "out": 2000}),
        _row("retrieve_quote-1", "deadbeef", model_id="b", model="m-b", usage={"in": 500, "out": 500}),
    ]
    answers.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    panel = {
        "a": {"provider": "openai", "model": "m-a", "endpoint": "h", "price_in": 1.0, "price_out": 2.0},
        "b": {"provider": "openai", "model": "m-b", "endpoint": "h", "price_in": 1.0, "price_out": 2.0},
    }
    u = score_file(answers, tmp_path / "scores.jsonl", panel=panel)["usage"]
    assert u["total"]["cost_usd"] == round(1500/1e6*1.0 + 2500/1e6*2.0, 6)  # all priced → total present


def test_score_rejects_digest_not_matching_questions(tmp_path):
    # answers carry digest "aaaa"; the roster/--questions digest is "bbbb" → refuse
    answers = tmp_path / "answers.jsonl"
    answers.write_text(json.dumps(_row("retrieve_quote-0", digest="aaaa")) + "\n")
    with pytest.raises(ScoreError, match="does not match"):
        score_file(answers, tmp_path / "scores.jsonl", expected_digest="bbbb")
    # matching digest scores fine
    summary = score_file(answers, tmp_path / "scores.jsonl", expected_digest="aaaa")
    assert summary["models"]["m1"]["_overall"]["n"] == 1


def test_score_rejects_missing_digest(tmp_path):
    answers = tmp_path / "answers.jsonl"
    answers.write_text(json.dumps(_row("retrieve_quote-0", digest=None)) + "\n")
    with pytest.raises(ScoreError) as e:
        score_file(answers, tmp_path / "scores.jsonl")
    assert "digest" in str(e.value)


def test_score_rejects_mixed_digests(tmp_path):
    answers = tmp_path / "answers.jsonl"
    answers.write_text(
        json.dumps(_row("retrieve_quote-0", digest="aaaa")) + "\n"
        + json.dumps(_row("retrieve_quote-1", digest="bbbb")) + "\n"
    )
    with pytest.raises(ScoreError) as e:
        score_file(answers, tmp_path / "scores.jsonl")
    assert "mixes" in str(e.value)


# --- single-candidate (anti-hedge) citation scoring --------------------------


def test_cite_passage_single_candidate():
    assert score_answer("cite_passage", "The citation is Jude 1:3.", {"citation": "Jude 1:3"})["correct"] == 1
    # same-number hedge
    assert score_answer("cite_passage", "It could be Jude 1:3, Jude 1:4, or Jude 1:5.",
                        {"citation": "Jude 1:3"})["correct"] == 0
    # CROSS-BOOK hedge (same verse numbers) must also fail — not numeric-only
    assert score_answer("cite_passage", "It could be John 1:1, Genesis 1:1, or Micah 1:1.",
                        {"citation": "John 1:1"})["correct"] == 0
    assert score_answer("cite_passage", "Either Jude 1:3 or John 1:3.",
                        {"citation": "Jude 1:3"})["correct"] == 0
    # near-miss must not pass via substring containment
    assert score_answer("cite_passage", "Jude 1:30", {"citation": "Jude 1:3"})["correct"] == 0


def test_cite_passage_incidental_numbers_not_false_hedge():
    # the extractor keys on the ground-truth SHAPE (colon), so an incidental version
    # year or "Chapter 1" is not a spurious second candidate for a correct answer
    assert score_answer("cite_passage", "The citation is Jude 1:3 (ASV 1901).", {"citation": "Jude 1:3"})["correct"] == 1
    assert score_answer("cite_passage", "The quote is from Jude 1:3. It appears in Chapter 1.", {"citation": "Jude 1:3"})["correct"] == 1


def test_cite_passage_lowercase_hedge_caught():
    # lowercase hedges must still be multi-candidate (case-insensitive extraction)
    assert score_answer("cite_passage", "it could be john 1:1 or genesis 1:1", {"citation": "John 1:1"})["correct"] == 0
    assert score_answer("cite_passage", "perhaps sahih al-bukhari 1, or sahih muslim 2", {"citation": "Sahih al-Bukhari 1"})["correct"] == 0


def test_cite_passage_paragraph_shape():
    # encyclical citations ("<Title>, para. N") — single correct vs hedge
    assert score_answer("cite_passage", "The citation is Rerum Novarum, para. 5.",
                        {"citation": "Rerum Novarum, para. 5"})["correct"] == 1
    assert score_answer("cite_passage", "maybe Rerum Novarum, para. 5 or Rerum Novarum, para. 6",
                        {"citation": "Rerum Novarum, para. 5"})["correct"] == 0
    assert score_answer("cite_passage", "Either Rerum Novarum para. 5 or Quadragesimo Anno para. 5",
                        {"citation": "Rerum Novarum, para. 5"})["correct"] == 0


def test_hadith_citation_single_and_hedge():
    # hadith citations have no colon ("Sahih al-Bukhari 1") — still anti-hedged
    assert score_answer("cite_passage", "Sahih al-Bukhari 1", {"citation": "Sahih al-Bukhari 1"})["correct"] == 1
    hedge = score_answer("cite_passage", "Sahih al-Bukhari 1 or Sahih Muslim 2",
                         {"citation": "Sahih al-Bukhari 1"})
    assert hedge["correct"] == 0 and hedge["n_candidates"] == 2


def test_suffixed_hadith_citation_single_and_hedge():
    # sunnah.com sub-hadith numbers carry an a/b suffix ("Sahih Muslim 2109a"). Before the fix,
    # _NUM_CITE's `(?![\d:ab])` tail extracted ZERO candidates from a suffixed number, so a hedge
    # fell through to bounded-equality and scored CORRECT (anti-hedge bypass). The suffix is now
    # part of the citation token.
    hedge = score_answer("cite_passage", "Either Sahih Muslim 2109a or Sahih Muslim 3311b",
                         {"citation": "Sahih Muslim 2109a"})
    assert hedge["correct"] == 0 and hedge["n_candidates"] == 2
    # a single suffixed answer still scores correct, and a wrong suffixed single is incorrect
    assert score_answer("cite_passage", "Sahih Muslim 2109a", {"citation": "Sahih Muslim 2109a"})["correct"] == 1
    assert score_answer("cite_passage", "Sahih Muslim 3311b", {"citation": "Sahih Muslim 2109a"})["correct"] == 0


def test_repeated_correct_citation_is_not_a_hedge():
    # a correct citation stated more than once is ONE candidate, not a hedge
    assert score_answer("cite_passage", "The citation is John 3:16 (John 3:16).", {"citation": "John 3:16"})["correct"] == 1
    assert score_answer("cite_passage", "This is Jude 1:3. Jude 1:3 warns believers.", {"citation": "Jude 1:3"})["correct"] == 1
    assert score_answer("cite_passage", "Rerum Novarum, para. 5. Yes, Rerum Novarum, para. 5.", {"citation": "Rerum Novarum, para. 5"})["correct"] == 1
    assert score_answer("cite_passage", "Sahih al-Bukhari 1. That is Sahih al-Bukhari 1.", {"citation": "Sahih al-Bukhari 1"})["correct"] == 1
    # but a repeat plus a DIFFERENT citation is still a hedge
    assert score_answer("cite_passage", "John 3:16. Or maybe John 3:17.", {"citation": "John 3:16"})["correct"] == 0


# --- raw-count overall + tradition aggregation -------------------------------


def _answer(qid, model, task, answer, expected, tradition, digest="d"):
    return {
        "question_id": qid, "model_id": model, "task": task, "answer": answer,
        "question_set_digest": digest,
        "question": {"expected": expected, "source": {"tradition": tradition}},
    }


def test_overall_is_raw_count(tmp_path):
    answers = tmp_path / "answers.jsonl"
    rows = [
        _answer("cite_passage-0", "m1", "cite_passage", "X 1:1", {"citation": "X 1:1"}, ["A"]),
        _answer("cite_passage-1", "m1", "cite_passage", "nope", {"citation": "X 1:2"}, ["A"]),
        _answer("cite_passage-2", "m1", "cite_passage", "nope", {"citation": "X 1:3"}, ["A"]),
        _answer("verify_source-0", "m1", "verify_source", "Yes", {"answer": "yes"}, ["A"]),
    ]
    answers.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    summary = score_file(answers, tmp_path / "scores.jsonl")
    ov = summary["models"]["m1"]["_overall"]
    assert ov["n"] == 4 and ov["accuracy"] == round(2 / 4, 4)  # 1 cite + 1 verify correct, raw


def test_tradition_counts_once_per_listed_tradition(tmp_path):
    answers = tmp_path / "answers.jsonl"
    rows = [
        _answer("cite_passage-0", "m1", "cite_passage", "X 1:1", {"citation": "X 1:1"}, ["Shared", "Xtrad"]),
        _answer("cite_passage-1", "m1", "cite_passage", "Y 1:1", {"citation": "Y 1:1"}, ["Shared", "Ytrad"]),
    ]
    answers.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    summary = score_file(answers, tmp_path / "scores.jsonl")
    assert summary["models"]["m1"]["_overall"]["n"] == 2  # overall counts each once
    by = summary["by_tradition"]["m1"]
    assert by["Shared"]["_overall"]["n"] == 2  # shared tradition sees both
    assert by["Xtrad"]["_overall"]["n"] == 1 and by["Ytrad"]["_overall"]["n"] == 1
    # per-tradition n sums above the overall count (the list-valued rule)
    assert by["Shared"]["_overall"]["n"] + by["Xtrad"]["_overall"]["n"] + by["Ytrad"]["_overall"]["n"] == 4 > 2
    md = summary_markdown(summary)
    assert "By tradition" in md and "Shared" in md


def test_missing_cell_rendered_as_dash(tmp_path):
    # m1 answered retrieve_quote only; m2 answered verify_source only -> each is
    # missing the other's task, shown as '—' (not dropped)
    answers = tmp_path / "answers.jsonl"
    rows = [
        _answer("retrieve_quote-0", "m1", "retrieve_quote", "x", {"text": "x"}, ["A"]),
        _answer("verify_source-0", "m2", "verify_source", "Yes", {"answer": "yes"}, ["A"]),
    ]
    answers.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    summary = score_file(answers, tmp_path / "scores.jsonl")
    assert "retrieve_quote" not in summary["models"]["m2"]  # m2 has no retrieve_quote
    md = summary_markdown(summary)
    assert "—" in md  # the missing cell is represented, not dropped


def test_missing_cells_with_roster(tmp_path):
    # the expected roster surfaces partially- and fully-missing/failed cells
    answers = tmp_path / "answers.jsonl"
    answers.write_text(json.dumps(_answer("retrieve_quote-0", "m1", "retrieve_quote", "x", {"text": "x"}, ["A"])) + "\n")
    expected = {("m1", "retrieve_quote"): 3, ("m1", "verify_source"): 2, ("m2", "retrieve_quote"): 3}
    summary = score_file(answers, tmp_path / "scores.jsonl", expected)
    m1 = summary["models"]["m1"]
    assert m1["retrieve_quote"]["n"] == 1 and m1["retrieve_quote"]["missing"] == 2
    vs = m1["verify_source"]
    assert vs["n"] == 0 and vs["missing"] == 2  # fully-missing task
    # a fully-missing cell carries the same three-outcome schema (counts 0, ratios None), distinct
    # from refused; coverage/accuracy/refused_rate are None (nothing answered)
    assert vs["correct"] == 0 and vs["incorrect"] == 0 and vs["refused"] == 0
    assert vs["accuracy"] is None and vs["coverage"] is None and vs["refused_rate"] is None
    assert "m2" in summary["models"]  # a model whose every cell failed still appears
    assert summary["models"]["m2"]["retrieve_quote"]["missing"] == 3
    assert summary["models"]["m2"]["retrieve_quote"]["refused"] == 0  # missing != refused
    assert summary["models"]["m2"]["_overall"]["missing"] == 3
    assert "miss" in summary_markdown(summary)


def test_missing_tradition_cell_represented(tmp_path):
    # a tradition-aware roster surfaces a model x tradition x task cell that failed
    # entirely (dropped from by_tradition without the roster)
    answers = tmp_path / "answers.jsonl"
    answers.write_text(json.dumps(_answer("rq-0", "m1", "retrieve_quote", "x", {"text": "x"}, ["A"])) + "\n")
    expected = {("m1", "retrieve_quote"): 2}
    expected_trad = {("m1", "A", "retrieve_quote"): 2, ("m1", "B", "retrieve_quote"): 2}
    summary = score_file(answers, tmp_path / "scores.jsonl", expected, expected_trad)
    by = summary["by_tradition"]["m1"]
    assert by["A"]["retrieve_quote"]["missing"] == 1  # 1 of 2 answered
    assert "B" in by and by["B"]["retrieve_quote"]["n"] == 0  # tradition B fully failed, still shown
    assert by["B"]["retrieve_quote"]["missing"] == 2


def test_summary_by_text_keyed_by_model_then_text(tmp_path):
    """Spec 26 per-text summary: keyed by model then text (work | version | language); a
    verify_source NEGATIVE aggregates under the ASKED edition (source), not the passage's source."""
    answers = tmp_path / "answers.jsonl"

    def row(qid, task, answer, expected, work, version, lang):
        return {
            "question_id": qid, "model_id": "m1", "task": task, "answer": answer,
            "question_set_digest": "d",
            "question": {"expected": expected,
                         "source": {"tradition": ["T"], "work": work, "version": version, "language": lang}},
        }

    rows = [
        row("rq-0", "retrieve_quote", "alpha beta gamma", {"text": "alpha beta gamma"}, "Qur", "U", "ar"),   # correct
        row("rq-1", "retrieve_quote", "wrong words here", {"text": "alpha beta gamma"}, "Qur", "U", "ar"),   # incorrect
        row("vs-0", "verify_source", "No, it is not.",
            {"answer": "no", "true_work": "Qur", "true_version": "U", "true_language": "ar"}, "Bukhari", "S", "ar"),
    ]
    answers.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    summary = score_file(answers, tmp_path / "scores.jsonl")

    bt = summary["by_text"]
    NUL = "\u0000"
    qur_key, bukhari_key = NUL.join(("Qur", "U", "ar")), NUL.join(("Bukhari", "S", "ar"))
    assert set(bt["m1"]) == {qur_key, bukhari_key}  # unambiguous (work, version, language) keys
    # the negative aggregates under the ASKED edition (Bukhari source), not its true source (Qur)
    assert bt["m1"][bukhari_key]["verify_source"]["n"] == 1
    assert "verify_source" not in bt["m1"][qur_key]
    qur = bt["m1"][qur_key]["retrieve_quote"]
    assert qur["n"] == 2 and qur["correct"] == 1 and qur["accuracy"] == 0.5
    md = summary_markdown(summary)
    assert "### By text" in md and "Bukhari (S, ar)" in md  # display form: work (version, language)


def test_by_text_key_is_unambiguous_no_collision(tmp_path):
    """Distinct (work, version, language) tuples that a ' | ' join would collide must stay separate
    (the NUL-joined key is unambiguous)."""
    answers = tmp_path / "answers.jsonl"

    def row(qid, work, version, lang):
        return {
            "question_id": qid, "model_id": "m1", "task": "retrieve_quote", "answer": "x",
            "question_set_digest": "d",
            "question": {"expected": {"text": "x"},
                         "source": {"tradition": ["T"], "work": work, "version": version, "language": lang}},
        }

    # ("A | B", "C", "D") and ("A", "B | C", "D") both render "A | B | C | D" under a naive join
    rows = [row("q0", "A | B", "C", "D"), row("q1", "A", "B | C", "D")]
    answers.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    summary = score_file(answers, tmp_path / "scores.jsonl")
    assert len(summary["by_text"]["m1"]) == 2  # two distinct texts, not one collapsed bucket
