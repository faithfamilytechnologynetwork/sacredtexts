"""Unit tests for the refusal matcher (Spec 15 phase 3, sacredbench.outcomes).

The pre-registered refused SET over the committed runs is pinned in
test_contains_reference_rebaseline.py; these tests exercise the matcher's logic directly.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from sacredbench.outcomes import (
    LEADING_WINDOW,
    _TEXT_RETRIEVAL,
    asserts_delivery,
    classify_refusal,
    leading_decline,
)

EXP = {"text": "The keeper planted twelve trees."}

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    "answer",
    [
        "I can't reliably reproduce that verse from memory.",
        "I cannot provide the exact text.",
        "I'm sorry, but I don't have that paragraph.",
        "I don't have access to that text.",
        "I couldn't retrieve the exact line from the edition.",
        "I couldn't verify the exact text of that passage.",
        "I can't help with that.",
        "I must decline to reproduce it.",
        "I can neither provide a quote from the Talmud nor a translation of it.",
    ],
)
def test_leading_declines_are_refusals(answer):
    assert leading_decline(answer) is True
    assert classify_refusal(answer, "retrieve_quote", EXP) is True


def test_decline_prefixed_but_delivers_is_not_refused():
    # containment half: delivers the verse despite a decline prefix -> NOT refused (mirrors the real
    # opus-search Ketubot 8a:8 cell retrieve_quote-4ad4392645da, which leads "I couldn't confirm…")
    ans = "I couldn't confirm the exact wording, but it is: The keeper planted twelve trees."
    assert leading_decline(ans) is True
    assert classify_refusal(ans, "retrieve_quote", EXP) is False


def test_deliver_then_caveat_is_not_refused():
    # the cue TRAILS the delivered verse (past the leading window) -> an answer with a disclaimer,
    # not a refusal. Mirrors the real tutorial cell fb0ce4da6218 (verse, then "(couldn't retrieve)").
    wrong = {"text": "a completely unrelated reference phrase goes here"}
    ans = ("The keeper planted twelve trees and watered them each morning without fail. "
           "(Note: I couldn't retrieve the source to verify.)")
    assert leading_decline(ans) is False  # cue sits past LEADING_WINDOW (verse delivered first)
    assert classify_refusal(ans, "retrieve_quote", wrong) is False


def test_cue_inside_delivered_verse_is_not_a_refusal():
    # "cannot" / "I will not" occur INSIDE real scripture; a delivered verse is never a refusal
    assert leading_decline("The social question cannot be reduced to economics.") is False
    assert classify_refusal("I will not forget thy word, O Lord.", "retrieve_quote",
                            {"text": "something else entirely"}) is False


def test_hedge_without_decline_cue_is_not_refused():
    # pure hedging ("I'm not sure", "best guess") is an attempt, not a refusal — those cues are
    # deliberately absent from the decline set
    ans = "I'm not certain, but my best guess is: The keeper planted nine trees."
    assert leading_decline(ans) is False
    assert classify_refusal(ans, "retrieve_quote", EXP) is False


def test_verify_source_refusal_is_parsed_based_not_classify_refusal():
    # Spec 26: verify_source refusal is "no leading verdict committed" (parsed is None), decided in
    # score._with_outcome — NOT classify_refusal (which now governs only text-retrieval / cite_passage).
    from sacredbench.score import score_answer

    # leads with the verdict (trailing decline) -> graded, even with a real decline cue present
    assert score_answer("verify_source", "No, I cannot verify that this is from X.",
                        {"answer": "no"})["outcome"] == "correct"
    # leads with a decline, verdict buried after "but" -> no leading verdict -> refused
    assert score_answer("verify_source", "I can't verify that, but no.", {"answer": "no"})["outcome"] == "refused"
    # a clean leading verdict -> graded
    assert score_answer("verify_source", "Yes, that is correct.", {"answer": "yes"})["outcome"] == "correct"


def test_leading_window_boundary():
    # a cue just inside the window is a refusal; padded past it is not
    pad = "x" * (LEADING_WINDOW - 5)
    assert leading_decline(pad + " i cannot provide this") is True
    far = "y" * (LEADING_WINDOW + 10)
    assert leading_decline(far + " i cannot provide this") is False


# ── Spec 48: assertion-based A/B refusal rule (web-search hedges) ─────────────────────────────────
#
# Pre-registered against runs/tutorial-2026-10-11/jev_agreement.json (the 11 refusal disagreements)
# plus the agreed-refusal anchors 42f510ea6c7d (0.58) / f143cc3f6c63 (0.68). A = delivered-as-answer
# (flips refused->incorrect); B = declined-with-substitute (stays refused). The architect's call
# (2026-10-29): B stays refused — the taxonomy asks "did the model purport to answer?".
TUTORIAL = REPO_ROOT / "runs" / "tutorial-2026-10-11"

A_CELLS = [  # (model_id, question_id) — positive identity assertion; must NOT be refused
    ("haiku-search", "retrieve_quote-e2d74279aaf0"),  # "from memory, the Uthmani text of 4:176 is:"
    ("opus-search", "retrieve_quote-d4c3bda0b400"),   # "my best reconstruction of the ... wording"
    ("opus-search", "retrieve_quote-d0239d95ae29"),   # "which most likely matches this line, is:"
    ("opus-search", "retrieve_quote-b33e7e040058"),   # "the line is probably: <he>"
    ("opus-search", "retrieve_quote-349b0b401f72"),   # "that baraita starts: <he>"
]
B_CELLS = [  # declined/substitute/unconfirmed — must stay refused
    ("opus-search", "retrieve_quote-f0ffc67a458e"),
    ("opus-search", "retrieve_quote-4c6f201c7192"),
    ("opus-search", "retrieve_quote-de9d77a6c963"),
    ("opus-search", "retrieve_quote-b1a04c81d33f"),
    ("opus-search", "retrieve_quote-fe52da70f661"),
    ("opus-search", "retrieve_quote-eaf381cf82d3"),
]
# Agreed refusals (judge AND deterministic), NOT in the 11 — textually identical to B members. A
# rule that flips the B twins but not these is overfit to the Jev oracle, so they are pinned here.
ANCHOR_CELLS = [
    ("opus-search", "retrieve_quote-42f510ea6c7d"),
    ("opus-search", "retrieve_quote-f143cc3f6c63"),
]

# Whole-corpus gate — each run's real on-disk layout as (run, scores, answers, questions). The
# strong check (test_spec48_classifier_reproduces_committed_refusals) recomputes the refusal OUTCOME
# from each answer + its expected text via the real classify_refusal and asserts it reproduces the
# committed refused set EXACTLY — catching both over- and under-firing on every run, incl. the Arabic
# run and complete_unit (which the byte re-score guards do not isolate on refusal).
TRIPLES = [
    ("tutorial-2026-10-11", "scores.jsonl", "answers.jsonl", "questions.jsonl"),
    ("first-run-2026-10-11", "scores.jsonl", "answers.jsonl", "questions.jsonl"),
    ("original-2026-10-21", "scores.jsonl", "answers.jsonl", "questions.jsonl"),
    ("exp-arabic-prompts-2026-10-29", "scores-en.jsonl", "answers-en.jsonl", "questions-en.jsonl"),
    # scores-ar.jsonl was produced from answers-ar-normalized.jsonl by the run's own analyze.py
    # (the orthography fold), so the gate must recompute over THAT file, not the un-normalized
    # answers-ar.jsonl (claude PR review). Inert today — the Arabic run has no refusals — but pairing
    # the score file with the answers it was actually scored from keeps the gate honest if it gains any.
    ("exp-arabic-prompts-2026-10-29", "scores-ar.jsonl", "answers-ar-normalized.jsonl", "questions-ar.jsonl"),
]


def _load_answers(run_dir: Path, fname: str = "answers.jsonl") -> dict:
    """Map (model_id, question_id) -> answer text from a committed run (read-only)."""
    path = run_dir / fname
    if not path.exists():
        pytest.skip(f"{path} not present")
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        out[(r.get("model_id"), r.get("question_id"))] = r.get("answer") or ""
    return out


def _load_expected_text(run_dir: Path, fname: str) -> dict:
    """Map question_id -> expected reference text from a run's questions file (read-only)."""
    path = run_dir / fname
    if not path.exists():
        pytest.skip(f"{path} not present")
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        out[r.get("id")] = (r.get("expected") or {}).get("text") or ""
    return out


@pytest.mark.parametrize("key", A_CELLS)
def test_spec48_delivered_as_answer_flips_out_of_refused(key):
    ans = _load_answers(TUTORIAL)[key]
    ref = _load_expected_text(TUTORIAL, "questions.jsonl").get(key[1], "")
    exp = {"text": ref}
    assert asserts_delivery(ans, ref) is True
    # with the real expected text (orthography variant => not bounded-contained), the assertion
    # escape — not the containment half — is what keeps these out of `refused`
    assert classify_refusal(ans, "retrieve_quote", exp) is False


def test_spec48_reworded_class_b_does_not_overfire():
    # A one-word rewording must not defeat the B exclusions: "closest/opening ... is: <script>" is a
    # DIFFERENT/adjacent span, not the requested unit, so it stays refused (guards every future run).
    he = "בראשית ברא אלהים"
    REF_B = "שלום עולם אחר"  # a Hebrew reference (so target script = Hebrew) NOT contained in the answers
    EXP_B = {"text": REF_B}
    for ans in (
        f"I couldn't find Ketubot 63b:19. The closest line I found is: {he}, but unconfirmed.",
        f"I couldn't find the exact segment. The opening text of the daf is: {he}",
        f"I couldn't find it. The preceding passage reads: {he}",
        # the reconstruction path must also reject a substitute modifier (codex iter-2)
        f"I couldn't find it. My best reconstruction of a different line is: {he}",
        f"I couldn't confirm it. My best reconstruction of the closest passage is: {he}",
        # ...and a negation INSIDE the reconstruction claim, not just before it (codex iter-3)
        f"I couldn't find it. My best reconstruction of what is probably not the requested line is: {he}",
        # ...and a disqualifier BETWEEN the reconstruction claim and a LATER payload (codex PR review):
        # the negation/non-identity sits past the claim's end but before the delivered script.
        f"I couldn't find it. My best reconstruction of the requested line is not reliable; the adjacent text is: {he}",
        # ...and a disclaimer TRAILING the payload within the same sentence (architect PR review).
        f"I couldn't find it. The line is: {he}, but that is a different line, not the requested one.",
    ):
        assert asserts_delivery(ans, REF_B) is False
        assert classify_refusal(ans, "retrieve_quote", EXP_B) is True


@pytest.mark.parametrize("key", B_CELLS)
def test_spec48_declined_with_substitute_stays_refused(key):
    ans = _load_answers(TUTORIAL)[key]
    ref = _load_expected_text(TUTORIAL, "questions.jsonl").get(key[1], "")
    # pass the REAL reference (Hebrew) so the guard logic — not an empty target script — is exercised
    assert asserts_delivery(ans, ref) is False
    assert classify_refusal(ans, "retrieve_quote", {"text": ref}) is True


def test_spec48_anti_overfit_anchor_matches_its_twins():
    # The 0.58/0.68 agreed refusals must be classified EXACTLY like their textually-identical B twins
    # de9d77a6c963 (0.45) / fe52da70f661 (0.47). Asserting them together is the anti-overfit guard.
    ans = _load_answers(TUTORIAL)
    exp = _load_expected_text(TUTORIAL, "questions.jsonl")
    for key in ANCHOR_CELLS + [("opus-search", "retrieve_quote-de9d77a6c963"),
                               ("opus-search", "retrieve_quote-fe52da70f661")]:
        assert classify_refusal(ans[key], "retrieve_quote", {"text": exp.get(key[1], "")}) is True, key


def test_spec48_from_memory_in_committed_refusals_is_not_a_delivery():
    # The blast-radius footgun: "from memory" appears in ~147 currently-refused cells, almost all
    # genuine declines ("I can't reliably reproduce ... from memory") — NOT the A-cell positive frame
    # ("From memory, the text of 4:176 IS:", which is now `incorrect`, not `refused`). Every
    # COMMITTED-REFUSED cell containing "from memory" must stay a non-delivery; assert the over-fire
    # complement is empty (a lower bound would let 144 of 147 over-fire silently).
    candidates, overfired = 0, []
    for run, sfile, afile, qfile in TRIPLES:
        run_dir = REPO_ROOT / "runs" / run
        spath = run_dir / sfile
        if not spath.exists():
            continue
        refused = {
            (r["model_id"], r["question_id"])
            for r in (json.loads(l) for l in spath.read_text(encoding="utf-8").splitlines() if l.strip())
            if r.get("task") in _TEXT_RETRIEVAL and r.get("metrics", {}).get("outcome") == "refused"
        }
        answers = _load_answers(run_dir, afile)
        expected = _load_expected_text(run_dir, qfile)
        for key in refused:
            if "from memory" in answers.get(key, "").lower():
                candidates += 1
                # pass the reference so the target script is the one the answer would have to deliver
                if asserts_delivery(answers[key], expected.get(key[1], "")) is not False:
                    overfired.append((run, key))
    assert candidates >= 3, f"expected >=3 committed-refused 'from memory' cells, saw {candidates}"
    assert overfired == [], f"committed refusals wrongly read as deliveries: {overfired}"


def test_spec48_edge_pointer_only_and_citation_echo_stay_refused():
    he = "בראשית"  # a Hebrew word, so a payload exists on the page
    ref_he = "שלום עולם אחר"  # Hebrew reference (target script), not contained in the answer
    exp_edge = {"text": ref_he}
    # hedge + pointer only (no assertion that the delivered text IS the passage) -> refused
    ans = f"I couldn't find the exact line. You can see it at sefaria.org/X. The daf begins with {he}."
    assert asserts_delivery(ans, ref_he) is False
    assert classify_refusal(ans, "retrieve_quote", exp_edge) is True
    # hedge + citation echo, no payload asserted as the answer -> refused
    ans2 = "I couldn't find Genesis 1:1. I can't give you that verse."
    assert asserts_delivery(ans2, ref_he) is False
    assert classify_refusal(ans2, "retrieve_quote", exp_edge) is True


def test_spec48_hedged_english_delivery_is_script_neutral():
    # Spec 48 / arch invariant (architect PR review): payload detection is NOT a Hebrew/Arabic/Greek
    # allowlist — the target script comes from the question's reference. A canonical LATIN-script
    # tradition (KJV, LDS) must be handled with no code edit. A hedged-then-DELIVERED English verse
    # that does not byte-contain the reference is a class-A delivery (scored, not refused); a genuine
    # English decline that points elsewhere is still refused.
    ref_en = "For God so loved the world, that he gave his only begotten Son"
    delivered = (
        "I couldn't find the exact KJV wording to verify. From memory, the verse reads: "
        "For God so loved the world, that he gave his one and only Son, so whoever believes."
    )
    assert asserts_delivery(delivered, ref_en) is True
    assert classify_refusal(delivered, "retrieve_quote", {"text": ref_en}) is False
    # a genuine English decline (no delivery frame, points to a source) stays refused
    decline = (
        "I can't reliably reproduce that verse from memory, and I don't want to give you a "
        "misquotation. You can find the official KJV text at biblegateway.com."
    )
    assert asserts_delivery(decline, ref_en) is False
    assert classify_refusal(decline, "retrieve_quote", {"text": ref_en}) is True
    # a true delivery that DOES byte-contain the reference is already correct (containment half),
    # so classify_refusal returns False via containment regardless of the assertion escape
    contained = f"I wasn't fully sure, but the verse reads: {ref_en}."
    assert classify_refusal(contained, "retrieve_quote", {"text": ref_en}) is False


@pytest.mark.parametrize("run,sfile,afile,qfile", TRIPLES)
def test_spec48_classifier_reproduces_committed_refusals(run, sfile, afile, qfile):
    # THE GATE: recompute the refusal OUTCOME from each answer + its expected text via the real
    # classify_refusal (gated on `correct`, exactly as score._with_outcome does) and assert it
    # reproduces the committed `refused` set for every _TEXT_RETRIEVAL cell. This catches BOTH
    # over-firing (a committed answer now read as a delivery) and under-firing (a new refusal) — the
    # strong form of the plan's "global refused-delta == flip set" gate, now that the committed
    # scores are post-rebaseline. Covers the Arabic run and complete_unit, which the byte re-score
    # guards do not isolate on the refusal dimension.
    run_dir = REPO_ROOT / "runs" / run
    spath = run_dir / sfile
    if not spath.exists():
        pytest.skip(f"{spath} not present")
    answers = _load_answers(run_dir, afile)
    expected = _load_expected_text(run_dir, qfile)
    committed_refused, predicted_refused = set(), set()
    for line in spath.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if r.get("task") not in _TEXT_RETRIEVAL:
            continue
        key = (r["model_id"], r["question_id"])
        m = r["metrics"]
        if m.get("outcome") == "refused":
            committed_refused.add(key)
        exp = {"text": expected.get(r["question_id"], "")}
        # mirrors score._with_outcome: refused = classify_refusal(...) AND not correct
        if classify_refusal(answers.get(key, ""), r["task"], exp) and not m.get("correct"):
            predicted_refused.add(key)
    assert predicted_refused == committed_refused, (
        f"{run}/{sfile}: classifier refusal set drifted from committed — "
        f"over: {predicted_refused - committed_refused}; under: {committed_refused - predicted_refused}"
    )
