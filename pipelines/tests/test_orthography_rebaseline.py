"""Spec 52 — witness that the Uthmani↔Imla'i orthography rebaseline moved ONLY the containment
headline, on EXACTLY the pre-registered cells, across EVERY committed run.

Sibling of ``test_contains_reference_rebaseline.py`` (first-run / tutorial headline flip sets) and
``test_refusal_rebaseline.py``. This oracle owns the Spec-52-specific guarantees over ALL five
committed score files — including ``original-2026-10-21`` and the ``exp-arabic-prompts-2026-10-29``
A/B, which the other oracles do not cover:

1. **Similarity frozen everywhere.** The ``(exact, normalized, token_f1)`` projection SHA of each
   committed score file is UNCHANGED from the pre-#52 base (origin/main ``b93e881``). The fold lives
   only in the containment predicate (``fold_aware_contains``); ``normalize()`` and all equality
   submetrics are byte-stable, so generation's ANCHOR digest and the copyright audit are untouched.
2. **Clean superset.** For every retrieve_quote / complete_unit cell in every run,
   ``correct == (normalized OR contains_reference)`` and ``normalized == 1 ⇒ contains_reference == 1``.
3. **Exactly the registered orthographic movers (by identity, not count).** The cells the fold newly
   credits are precisely those with ``contains_reference == 1`` while the pre-#52 word-bounded
   ``bounded_contains`` is False — credited BY the orthography fold, not pre-existing containment.
   Their exact ``(model_id, question_id)`` set is pinned per run (hand-verified, Spec 52 review); a
   compensating add/remove swap cannot pass. Every one is ``correct == 1`` (the fold only adds).
4. **Derived summaries agree with their scores.** ``summary.json`` per-model/per-task
   accuracy/coverage/correct recomputed from ``scores.jsonl`` match — guards the surgical summary
   splices (the aspir-48 scar) for runs with no other durable summary pin (notably ``original``).
5. **The experiment recovers.** Under the fold both models in BOTH conditions of the exp A/B score
   27/28, and 0 of 56 cells flip between en and ar — the ~8-11pt Arabic-prompt drop was a scorer
   artifact. (The exp mover identities are pinned too.)

Read-only; re-derives containment from the committed answers. Skips cleanly if evidence is absent.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from sacredbench.score import _is_arabic_letter, bounded_contains, fold_aware_contains, normalize

REPO_ROOT = Path(__file__).resolve().parents[2]

SIM_PROJECTION_SHA256 = {
    # Re-pinned when normalize() stopped splitting Latin diacritics (Yoḥanan, Ismāʿīl,
    # café). exact and normalized did not move; token_f1 did, on 12 cells.
    "tutorial-2026-10-11/scores.jsonl": "20c5c0597283cfc1fcde1dd6844b18fdfcf130f9032d4868f7956d129afafa2d",
    "original-2026-10-21/scores.jsonl": "ba45b9f4ca62fc3b45365f490ac0d26518ac46f4a27a289708c868993812ab81",
    "first-run-2026-10-11/scores.jsonl": "bf52500cf18c2b630c3c6e9bd01268de6b3f3472d4cd79a61db36e24ce9f0fdc",
    "exp-arabic-prompts-2026-10-29/scores-ar.jsonl": "c369e76ad5d40baf819b523ced13d9fdabedbe5e84d55a8daeaeadf8912ca580",
    "exp-arabic-prompts-2026-10-29/scores-en.jsonl": "83d57ee5f3f14135022ddb51d93f3bd744e4887f80ef6948a5ce14735dab1259",
}

# Exact (model_id, question_id) sets the orthography fold newly credits, per run. Hand-verified
# against each verse (Spec 52 review). Total = 56 (tutorial 20, original 15, first-run 0, exp-ar 12,
# exp-en 9). [Was 58: the item-1 whitespace tightening (PR #62 review) removed 2 accidental exp-ar
# over-credits on retrieve_quote-317f7f727f3c — the #60 ءَآ↔آ residual, now in HAMZA_ALEF_RESIDUAL.]
# Each run: (scores file, answers file to re-derive containment from).
_EMPTY: set = set()
ORTHO_MOVERS = {
    "tutorial": ("tutorial-2026-10-11/scores.jsonl", "tutorial-2026-10-11/answers.jsonl", {
        ("haiku", "retrieve_quote-1e51194b8420"), ("haiku", "retrieve_quote-528c5b83569e"),
        ("haiku", "retrieve_quote-571bf774a203"), ("haiku", "retrieve_quote-60993d0becf0"),
        ("haiku", "retrieve_quote-66d7a26e7e93"), ("haiku", "retrieve_quote-91c4ddd54da1"),
        ("haiku", "retrieve_quote-b70583402f8f"), ("haiku", "retrieve_quote-c211a13b8670"),
        ("haiku", "retrieve_quote-f4e378e5065d"), ("haiku", "retrieve_quote-fb0ce4da6218"),
        ("haiku", "retrieve_quote-fd566a54bc82"), ("haiku-search", "retrieve_quote-528c5b83569e"),
        ("haiku-search", "retrieve_quote-60993d0becf0"), ("haiku-search", "retrieve_quote-66d7a26e7e93"),
        ("haiku-search", "retrieve_quote-b70583402f8f"), ("haiku-search", "retrieve_quote-e2d74279aaf0"),
        ("haiku-search", "retrieve_quote-ed21c10a072e"), ("haiku-search", "retrieve_quote-f4e378e5065d"),
        ("haiku-search", "retrieve_quote-fb0ce4da6218"), ("haiku-search", "retrieve_quote-fd566a54bc82"),
    }),
    "original": ("original-2026-10-21/scores.jsonl", "original-2026-10-21/answers.jsonl", {
        ("haiku", "complete_unit-b730bac6761f"), ("haiku", "complete_unit-e75db63cb3f6"),
        ("haiku", "retrieve_quote-2fd43836a10b"), ("haiku", "retrieve_quote-5d482247f058"),
        ("haiku", "retrieve_quote-ab683e42cd74"), ("haiku", "retrieve_quote-d0747fb44a9a"),
        ("haiku", "retrieve_quote-d15c8a86c98f"), ("opus", "complete_unit-21f35e0211cd"),
        ("opus", "complete_unit-a722a33ea0c4"), ("opus", "complete_unit-e8bf210912d8"),
        ("opus", "complete_unit-f1ba80f1a064"), ("opus", "retrieve_quote-5d482247f058"),
        ("opus", "retrieve_quote-ab683e42cd74"), ("opus", "retrieve_quote-d0747fb44a9a"),
        ("opus", "retrieve_quote-d15c8a86c98f"),
    }),
    "first-run": ("first-run-2026-10-11/scores.jsonl", "first-run-2026-10-11/answers.jsonl", _EMPTY),
    "exp-ar": ("exp-arabic-prompts-2026-10-29/scores-ar.jsonl",
               "exp-arabic-prompts-2026-10-29/answers-ar-normalized.jsonl", {
        ("sol", "complete_unit-b730bac6761f"), ("sol", "retrieve_quote-2fd43836a10b"),
        ("sol", "retrieve_quote-5d482247f058"),
        ("sol", "retrieve_quote-ab683e42cd74"), ("sol", "retrieve_quote-d0747fb44a9a"),
        ("sol", "retrieve_quote-d15c8a86c98f"), ("sonnet", "complete_unit-b730bac6761f"),
        ("sonnet", "retrieve_quote-2fd43836a10b"),
        ("sonnet", "retrieve_quote-5d482247f058"), ("sonnet", "retrieve_quote-ab683e42cd74"),
        ("sonnet", "retrieve_quote-d0747fb44a9a"), ("sonnet", "retrieve_quote-d15c8a86c98f"),
    }),
    "exp-en": ("exp-arabic-prompts-2026-10-29/scores-en.jsonl",
               "exp-arabic-prompts-2026-10-29/answers-en.jsonl", {
        ("sol", "complete_unit-b730bac6761f"), ("sol", "retrieve_quote-5d482247f058"),
        ("sol", "retrieve_quote-ab683e42cd74"), ("sol", "retrieve_quote-d0747fb44a9a"),
        ("sonnet", "retrieve_quote-2fd43836a10b"), ("sonnet", "retrieve_quote-5d482247f058"),
        ("sonnet", "retrieve_quote-ab683e42cd74"), ("sonnet", "retrieve_quote-d0747fb44a9a"),
        ("sonnet", "retrieve_quote-d15c8a86c98f"),
    }),
}

_TEXT_TASKS = ("retrieve_quote", "complete_unit")

# PRE-REGISTERED known-residual set (Spec 52, architect-approved defer 2026-10-29): committed cells
# the fold leaves UNDER-credited because word-initial hamza-alef «ءَا» (Uthmani) ≠ alef-madda «آ»
# (Imla'i) — the answer is the correct verse, in an orthography the containment fold does not yet
# equate. All are `contains_reference == 0` today; the follow-up fold extension (collapse «ء+ا»↔«آ»)
# inherits this as its ready-made oracle (these flip to credited when it lands). Tracked in the
# follow-up issue referenced from the PR body and run READMEs. NOTE the tutorial asymmetry: on the
# SAME verse, haiku-search wrote «ءَا» (credited) while haiku wrote «آ» (here, uncredited) — so part
# of the committed haiku→haiku-search "search lift" is this orthography residual, not retrieval.
HAMZA_ALEF_RESIDUAL = {
    "tutorial-2026-10-11/scores.jsonl": {
        ("haiku", "retrieve_quote-1d74fc87541b"),   # 8:52 «ءَالِ» vs haiku «آلِ» (haiku-search credited)
        ("haiku", "retrieve_quote-a8df3e43d35d"),   # 2:285 «ءَامَنَ» vs haiku «آمَنَ» (haiku-search credited)
    },
    "original-2026-10-21/scores.jsonl": {
        ("haiku", "retrieve_quote-8c4ce779621f"),   # 14:34 «وَءَاتَىٰكُم» vs «وَآتَاكُم»
        ("opus", "retrieve_quote-8c4ce779621f"),
    },
    "exp-arabic-prompts-2026-10-29/scores-ar.jsonl": {
        ("sonnet", "retrieve_quote-8c4ce779621f"), ("sol", "retrieve_quote-8c4ce779621f"),
        # 27:59 «ءَآللَّهُ» — the AR scaffold elicits Imla'i «آللَّهُ» (madda) → the same ءَا↔آ residual.
        # EXPOSED by the item-1 whitespace tightening (PR #62 review): the old over-permissive \s*
        # was accidentally bridging this uncovered #60 gap via the plene form; the tightened predicate
        # correctly leaves it uncredited. ASYMMETRIC: the EN answers wrote «ءَآللَّهُ» and STAY credited
        # (so this pair is NOT in the scores-en set), which is why exp lands en 96.4% / ar 92.9% with a
        # single residual cross-condition flip on this question.
        ("sonnet", "retrieve_quote-317f7f727f3c"), ("sol", "retrieve_quote-317f7f727f3c"),
    },
    "exp-arabic-prompts-2026-10-29/scores-en.jsonl": {
        ("sonnet", "retrieve_quote-8c4ce779621f"), ("sol", "retrieve_quote-8c4ce779621f"),
    },
}

# SECOND pre-registered residual class (PR #62 review item 2, claude): a verbatim-correct āyah left
# uncredited because the VERSE-NUMBER SIGN is glued to the final word (U+06DD end-of-āyah + the
# Arabic-Indic digits, e.g. «…عليم۝١٧٦»), breaking the trailing word boundary of the word-bounded
# containment. Distinct from HAMZA_ALEF_RESIDUAL (a letter-identity gap) — this is a tokenisation gap.
# `contains_reference == 0` today; the fix (strip a trailing verse-number before the boundary match)
# is DEFERRED to #60, which inherits this cell alongside the hamza-alef set as its before/after oracle.
# On the tutorial run this is the third of haiku-off's three Qur'an misses — all three scorer
# residuals, zero genuine — so the apparent haiku→haiku-search Qur'an "search lift" is entirely
# artifactual (see runs/tutorial-2026-10-11/README.md).
VERSE_NUMBER_RESIDUAL = {
    "tutorial-2026-10-11/scores.jsonl": {
        ("haiku", "retrieve_quote-e2d74279aaf0"),   # 4:176, «…عليم۝١٧٦» — verse number glued to عليم
    },
}

# Arabic-cell partition pin (drift guard, Phase-2 deliverable). An "Arabic cell" is one whose ANSWER
# or EXPECTED text carries an Arabic-script LETTER (``_is_arabic_letter``: category L in the Arabic
# blocks — NOT Arabic-Indic digits, NOT Arabic punctuation, so the count is stable and unambiguous).
# Pinned per run as (arabic_expected, arabic_either); guards a corpus/question-set change that would
# alter the fold's potential domain even if no cell happens to move. Keyed by (scores, answers).
ARABIC_CELLS = {
    "tutorial": ("tutorial-2026-10-11/answers.jsonl", (132, 132)),
    "original": ("original-2026-10-21/answers.jsonl", (420, 459)),
    "first-run": ("first-run-2026-10-11/answers.jsonl", (0, 2)),
    "exp-ar": ("exp-arabic-prompts-2026-10-29/answers-ar-normalized.jsonl", (28, 28)),
    "exp-en": ("exp-arabic-prompts-2026-10-29/answers-en.jsonl", (28, 29)),
}


def _rows(path: str):
    p = REPO_ROOT / "runs" / path
    if not p.exists():
        pytest.skip(f"{path} not present")
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def _answers(path: str):
    p = REPO_ROOT / "runs" / path
    if not p.exists():
        pytest.skip(f"{path} not present")
    return {
        (d["model_id"], d["question_id"]): (d["answer"], d["question"]["expected"])
        for d in (json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip())
    }


@pytest.mark.parametrize("path", list(SIM_PROJECTION_SHA256))
def test_similarity_projection_frozen(path):
    proj = sorted(
        (r["model_id"], r["question_id"], r["task"],
         r["metrics"].get("exact"), r["metrics"].get("normalized"), r["metrics"].get("token_f1"))
        for r in _rows(path)
    )
    digest = hashlib.sha256(json.dumps(proj, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    assert digest == SIM_PROJECTION_SHA256[path], (
        f"{path}: exact/normalized/token_f1 projection moved — the fold must not touch a similarity tier"
    )


@pytest.mark.parametrize("path", [
    "tutorial-2026-10-11/scores.jsonl", "original-2026-10-21/scores.jsonl",
    "first-run-2026-10-11/scores.jsonl",
])
def test_headline_is_a_clean_superset(path):
    for r in _rows(path):
        if r["task"] not in _TEXT_TASKS:
            continue
        m = r["metrics"]
        if "contains_reference" not in m:
            continue
        if m.get("normalized") == 1:
            assert m["contains_reference"] == 1, "normalized=1 must imply contains_reference=1"
        assert m["correct"] == int(bool(m.get("normalized")) or bool(m["contains_reference"]))


@pytest.mark.parametrize("run", list(ORTHO_MOVERS))
def test_orthographic_movers_are_exactly_the_registered_set(run):
    scores, answers, registered = ORTHO_MOVERS[run]
    ans = _answers(answers)
    found = set()
    for r in _rows(scores):
        if r["task"] not in _TEXT_TASKS or r["metrics"].get("contains_reference") != 1:
            continue
        a, expected = ans[(r["model_id"], r["question_id"])]
        target = expected["text"]
        # credited BY the fold: fold_aware_contains holds but pre-#52 bounded_contains does not.
        if normalize(target) and fold_aware_contains(a, target) and not bounded_contains(a, target):
            found.add((r["model_id"], r["question_id"]))
            assert r["metrics"]["correct"] == 1, "a fold-credited cell must be correct"
    assert found == registered, (
        f"{run}: orthographic movers differ from the registered set — "
        f"unexpected {sorted(found - registered)}, missing {sorted(registered - found)}"
    )


@pytest.mark.parametrize("run", ["tutorial-2026-10-11", "original-2026-10-21"])
def test_summary_agrees_with_scores(run):
    # Recompute the per-model/per-task headline from scores.jsonl and check it matches the committed
    # summary.json — guards the surgical summary splice (original has no other durable pin).
    scores = _rows(f"{run}/scores.jsonl")
    sp = REPO_ROOT / "runs" / run / "summary.json"
    if not sp.exists():
        pytest.skip(f"{run} summary absent")
    summary = json.loads(sp.read_text(encoding="utf-8"))
    agg: dict = {}
    for r in scores:
        c = agg.setdefault((r["model_id"], r["task"]), [0, 0, 0])  # correct, incorrect, refused
        o = r["metrics"]["outcome"]
        c[0 if o == "correct" else 1 if o == "incorrect" else 2] += 1
    # also roll up each model's _overall (sum across its tasks)
    overall: dict = {}
    for (mid, _task), c in agg.items():
        o = overall.setdefault(mid, [0, 0, 0])
        for i in range(3):
            o[i] += c[i]

    def _check(leaf, corr, inc, ref, where):
        n = corr + inc + ref
        acc = None if (corr + inc) == 0 else round(corr / (corr + inc), 4)
        cov = round((corr + inc) / n, 4)
        assert leaf["correct"] == corr and leaf["incorrect"] == inc and leaf["refused"] == ref, \
            f"{where}: summary counts disagree with scores"
        assert leaf["accuracy"] == acc and leaf["coverage"] == cov, \
            f"{where}: summary accuracy/coverage disagree with scores"

    for (mid, task), (corr, inc, ref) in agg.items():
        _check(summary["models"][mid][task], corr, inc, ref, f"{run} {mid}/{task}")
    for mid, (corr, inc, ref) in overall.items():
        _check(summary["models"][mid]["_overall"], corr, inc, ref, f"{run} {mid}/_overall")


@pytest.mark.parametrize("run", list(ARABIC_CELLS))
def test_arabic_cell_partition_pinned(run):
    answers, (exp_arabic, either_arabic) = ARABIC_CELLS[run]
    rows = _answers(answers)
    n_exp = n_either = 0
    for _key, (answer, expected) in rows.items():
        et = expected.get("text") or expected.get("citation") or ""
        a = any(_is_arabic_letter(c) for c in answer)
        e = any(_is_arabic_letter(c) for c in et)
        n_exp += int(e)
        n_either += int(a or e)
    assert n_exp == exp_arabic, f"{run}: arabic-expected cells = {n_exp}, pinned {exp_arabic}"
    assert n_either == either_arabic, f"{run}: arabic-either cells = {n_either}, pinned {either_arabic}"


@pytest.mark.parametrize("path", list(HAMZA_ALEF_RESIDUAL))
def test_hamza_alef_residual_is_pre_registered_and_uncredited(path):
    # The 8 known hamza-alef↔madda under-credits are pinned by identity and are all currently
    # uncredited (contains_reference == 0). This is the follow-up fold's ready-made oracle: when the
    # «ء+ا»↔«آ» extension lands, these flip to 1 and this assertion is updated, cell-for-cell.
    by_key = {(r["model_id"], r["question_id"]): r["metrics"] for r in _rows(path)}
    for key in HAMZA_ALEF_RESIDUAL[path]:
        assert key in by_key, f"{path}: residual cell {key} absent"
        assert by_key[key].get("contains_reference") == 0, (
            f"{path}: residual cell {key} is now credited — if the hamza-alef fold extension landed, "
            "move it out of HAMZA_ALEF_RESIDUAL and into the credited sets"
        )


@pytest.mark.parametrize("path", list(VERSE_NUMBER_RESIDUAL))
def test_verse_number_residual_is_pre_registered_and_uncredited(path):
    # The verbatim-correct āyah(s) uncredited only because a trailing verse-number sign breaks the
    # word boundary (second residual class). All `contains_reference == 0` today; #60's digit-strip
    # fix flips them, cell-for-cell. Independent sanity: stripping a trailing verse-number from the
    # answer credits the cell (so the ONLY blocker is the glued number).
    import re as _re
    from sacredbench.score import fold_aware_contains
    by_key = {(r["model_id"], r["question_id"]): r["metrics"] for r in _rows(path)}
    ans = _answers(path.replace("scores.jsonl", "answers.jsonl"))
    for key in VERSE_NUMBER_RESIDUAL[path]:
        assert key in by_key, f"{path}: residual cell {key} absent"
        assert by_key[key].get("contains_reference") == 0, (
            f"{path}: verse-number residual {key} is now credited — if #60's digit-strip landed, "
            "move it out of VERSE_NUMBER_RESIDUAL"
        )
        answer, expected = ans[key]
        stripped = _re.sub(r"[۝٠-٩۰-۹\d]+\s*$", "", answer.strip())
        assert fold_aware_contains(stripped, expected["text"]), (
            f"{path}: {key} is NOT credited even after stripping the trailing verse-number — "
            "its miss is more than the digit glue, so this pin is mis-attributed"
        )


def test_exp_arabic_prompt_artifact_is_resolved():
    # The ~8–11pt Arabic-prompt accuracy drop was almost entirely a scorer artifact and resolves under
    # the fold — DOWN TO a single pre-registered residual cell. EN reaches 27/28 per model (96.4%); AR
    # reaches 26/28 (92.9%) because of ONE residual cross-condition flip: retrieve_quote-317f7f727f3c
    # (Q27:59) for BOTH models, a #60 hamza-alef «ءَآ↔آ» cell (the AR scaffold elicits Imla'i «آللَّهُ»),
    # NOT a retrieval difference. This pins the full before/after oracle for #60's eventual fold:
    # when «ءَآ↔آ» lands, this flip closes and AR rejoins EN at 96.4%. (PR #62 review items 1–2.)
    en = {(r["model_id"], r["question_id"]): r for r in _rows("exp-arabic-prompts-2026-10-29/scores-en.jsonl")}
    ar = {(r["model_id"], r["question_id"]): r for r in _rows("exp-arabic-prompts-2026-10-29/scores-ar.jsonl")}
    assert en.keys() == ar.keys() and len(en) == 56
    en_correct = {mid: 0 for (mid, _q) in en}
    ar_correct = {mid: 0 for (mid, _q) in ar}
    for (mid, _q), r in en.items():
        en_correct[mid] += int(r["metrics"]["outcome"] == "correct")
    for (mid, _q), r in ar.items():
        ar_correct[mid] += int(r["metrics"]["outcome"] == "correct")
    assert set(en_correct.values()) == {27}, f"EN expected 27 correct/model, got {en_correct}"
    assert set(ar_correct.values()) == {26}, f"AR expected 26 correct/model, got {ar_correct}"
    # exactly one question flips en→ar, for both models, and it is the pre-registered #60 residual
    flips = {k for k in en if en[k]["metrics"]["outcome"] != ar[k]["metrics"]["outcome"]}
    assert flips == {("sonnet", "retrieve_quote-317f7f727f3c"), ("sol", "retrieve_quote-317f7f727f3c")}, (
        f"unexpected en↔ar flip set: {flips}"
    )
    for k in flips:
        assert en[k]["metrics"]["outcome"] == "correct" and ar[k]["metrics"]["outcome"] == "incorrect"
        assert ("sonnet" if k[0] == "sonnet" else "sol", k[1]) in HAMZA_ALEF_RESIDUAL[
            "exp-arabic-prompts-2026-10-29/scores-ar.jsonl"]
