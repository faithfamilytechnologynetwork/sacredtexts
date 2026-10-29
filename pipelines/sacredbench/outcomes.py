"""Outcome classification (Spec 15, decision #2): refusal is an OUTCOME, not a grader.

Every answered cell gets ``outcome`` ∈ {``correct``, ``incorrect``, ``refused``}. A **refusal** is
detected here, in the outcome layer, and **short-circuits the headline verdict** — a cell the model
declined to answer is neither right nor wrong, so it is excluded from accuracy (``accuracy =
correct/(correct+incorrect)``) and surfaced as ``coverage`` / ``refused_rate`` instead. Graders
(``graders.py``) only ever decide correct-vs-incorrect for the cells that were actually answered.

Refusal rule (deterministic, pre-registered against the committed runs' ``answers.jsonl`` — see
``tests/test_contains_reference_rebaseline.py`` for the frozen (model_id, question_id) set and the
per-model counts this matcher must reproduce):

    a cell is ``refused`` iff a **decline cue appears in the leading segment of the answer**
    (the first ``LEADING_WINDOW`` normalized characters) **AND** the expected reference is **not**
    delivered. The cue list is English. A decline in Greek, Hebrew, or Arabic that does not use
    one of these phrases is not classified as refused, so refusal rates are not comparable across
    scripts.

Both halves matter:

- *decline cue* — a conservative set of first-person inability / non-delivery / refusal markers
  (``DECLINE_CUES``). They are matched against the normalized answer, so case and punctuation
  (including the apostrophe in ``can't``) fold automatically.
- *leading segment* — the cue must OPEN the answer, not trail it. An answer that delivers the verse
  and then appends a caveat ("…verse… (I couldn't retrieve the source to verify)") is an ANSWER with
  a disclaimer, not a refusal; its cue sits past the delivered text, outside the leading window. In
  the committed runs 262/266 declines open at character 0; the window only has to clear the longest
  genuine preamble ("I'm sorry, but I am unable…", "Let me try to get the segment. I couldn't…").
- *reference not delivered* — a decline-prefixed answer that still contains the reference
  (word-bounded) IS a correct retrieval ("I can't be certain, but it's: <verse>"), so the containment
  half keeps it out of the refused set. **Spec 48** adds a second escape for text-retrieval: an answer
  that does not byte-contain the reference but POSITIVELY ASSERTS the delivered original-script
  payload is the requested passage ("from memory the text of 4:176 is: …", "my best reconstruction …
  is: …", "that baraita starts: …") is an answer with an orthography disclaimer (class A), not a
  refusal — see ``asserts_delivery``. A declined-with-a-substitute answer (class B — "the closest I
  got was a different line", "the daf begins with …", "I can't say it's segment X") carries no such
  assertion and stays refused. This is **assertion-only**, not "assertion and no disclaimer" (an A
  answer can disclaim the *segment number* in a separate clause), and it is the paper-facing refusal
  definition that deliberately diverges from the looser Jev rubric criterion (re-aligned in a future
  ``sacredbench-jev-2``). For ``cite_passage`` a leading decline alone is the refusal, gated on
  ``not correct`` so a decline-prefixed but delivered citation stays an answer.
  ``verify_source`` is **not** classified here (Spec 26): its "answer" is the verdict itself, so its
  refusal is ``parsed is None`` (no leading Yes/No committed), decided in ``score._with_outcome`` — a
  committed leading verdict is graded even with a trailing disclaimer, and a negation-evasion with no
  leading verdict is refused, not scored correct.

This module is deliberately thin: the primitives (``normalize``, ``bounded_contains``, ``parse_yes_no``)
live in ``score.py`` and are imported lazily so there is no import cycle (``score`` imports this inside
``score_answer``).
"""

from __future__ import annotations

import re
from functools import lru_cache

# The leading segment (in normalized characters) a decline cue must fall within to count as a
# refusal. Round and robust: it clears the genuine preambles (longest observed ≈ 39) while excluding
# the deliver-then-caveat cells (earliest trailing caveat observed ≈ 71).
LEADING_WINDOW = 60

# Conservative first-person inability / non-delivery / refusal cues, in natural form. They are
# normalized before matching (``score.normalize``), so "can't" → "can t", case folds, and punctuation
# is stripped — a cue is compared against the normalized answer. The set is intentionally narrow:
# each phrase states that the model is NOT delivering the text (not mere hedging like "I'm not sure"
# or "best reconstruction", which accompany a delivered guess and must stay OUT of the refused set).
_DECLINE_CUES_RAW: tuple[str, ...] = (
    # cannot / can't reproduce · provide · give · share the text
    "i can't reliably", "i cannot reliably", "i can't reproduce", "i cannot reproduce",
    "i can't give you the exact", "i can't give the exact", "i can't give you that",
    "i cannot give you the exact", "i can't provide", "i cannot provide",
    "i'm not able to provide", "i am not able to provide", "i'm unable to provide",
    "i am unable to provide", "unable to provide", "not able to provide",
    "i can't share", "i cannot share",
    # no access / don't have it
    "i don't have access", "i do not have access", "don't have access",
    "i don't have that", "i do not have that", "i don't have the exact", "i do not have the exact",
    "i don't have the capability", "i don't have a reliable", "i don't have a dependable",
    "i don't have a verified copy", "i don't have it memorized",
    # sorry-but-no
    "i'm sorry, but i don't", "i'm sorry but i don't", "i'm sorry, but i can't",
    "i'm sorry but i can't", "i can't help with that", "i can't fulfill", "i cannot fulfill",
    # "I can neither provide … nor …" — a two-part decline (surfaced by the iter-2 review)
    "i can neither",
    # cannot / couldn't verify · recall · find · confirm · retrieve · get
    "i'm unable to verify", "i am unable to verify", "i'm not able to verify",
    "i am not able to verify", "i can't verify", "i cannot verify",
    "i couldn't verify", "i could not verify",
    "i couldn't retrieve", "i couldn't confirm", "i couldn't get", "i couldn't find",
    "i could not retrieve", "i could not confirm",
    # can't confirm / pinpoint / confidently give — first-person inability to cite a passage the
    # model acknowledges exists (Spec-26 cite_passage survey: these led the answer but were
    # classified `incorrect` rather than `refused`). A confident third-person NON-existence claim
    # ("Not found in the KJV", "No such verse") is a wrong answer, not a decline, and stays out.
    "i can't confirm", "i cannot confirm", "i can't pinpoint", "i cannot pinpoint",
    "i can't confidently give", "i cannot confidently give",
    # explicit refusal
    "i must decline", "i won't provide", "i will not provide", "i won't reconstruct",
    "i can't access", "i cannot access",
)

_TEXT_RETRIEVAL = ("retrieve_quote", "complete_unit")

# ── Delivery-assertion test (Spec 48) ────────────────────────────────────────────────────────────
# A web-search answer may OPEN with a decline cue ("I couldn't find the exact edition…") and then
# either (A) deliver the requested passage as its answer, however hedged ("from memory the text of
# 4:176 IS: …", "my best reconstruction … IS: …", "that baraita STARTS: …"), or (B) offer a
# DIFFERENT / unconfirmed span and explicitly disclaim it as the requested one ("the closest I got
# was a different line", "the daf begins with …", "I can't say it's segment X", "I'm not sure which
# part counts as segment 3"). (A) purported to answer → scored on its merits; (B) declined → refused.
#
# The test is **assertion-only**, not "assertion AND no disclaimer": an A answer can itself carry a
# disclaimer in a *different* clause ("I'm not sure which passage is segment 9. What follows is my
# best reconstruction …"), so a global no-disclaimer gate would wrongly strand it as refused. We
# instead look for a POSITIVE delivery assertion and reject it only if the negation sits inside the
# assertion's own clause. It is also frame-anchored and negation-aware so a bare "from memory" under
# a decline ("I can't reliably reproduce … from memory") does not count as a delivery.

# Target-script run (Hebrew, Arabic incl. presentation forms, Greek) — a delivered scripture payload.
# A positive delivery must introduce actual original-script text (conservative: an English-only
# gloss is not a delivery), which is also what keeps delivery *volume* from being the signal.
#
# LIMITATION (Spec 48): this is a Hebrew/Arabic/Greek ALLOWLIST. A hedged-but-delivering answer in
# any other script — including **Latin** (a confabulated non-containing English/Latin delivery) —
# is not recognised as a payload and stays `refused`, so the original false-`refused` bug survives
# on that axis for a Latin-script tradition. Adding such a tradition would require EXTENDING this
# range (the one spot where a new tradition touches core pipeline code — cf. arch-critical). The
# ranges are approximate letter blocks; the Arabic block also admits harakat / Arabic-Indic digits,
# which is harmless because `_ASSERT_INTRO`/`_ASSERT_RECON` still require a positive assertion frame.
# The presentation-forms-B range stops at U+FEFE so the BOM (U+FEFF) is excluded, and the Hebrew
# range starts at the alef (U+05D0) so lone cantillation/punctuation marks do not read as a payload.
_SCRIPT = (
    "א-תׯ-״ؠ-ۿݐ-ݿࢠ-ࣿ"
    "יִ-﷿ﹰ-﻾Ͱ-Ͽἀ-῿"
)
_SCRIPT_CHAR = re.compile(f"[{_SCRIPT}]")

# Nouns a positive assertion is ABOUT: the requested unit itself. Deliberately EXCLUDES "segment",
# "daf", "page" — the B answers describe *those* ("the daf begins with…", "which part is segment 3"),
# not the requested line.
_UNIT = r"(?:line|text|verse|passage|baraita|baraisa|mishnah|mishna|gemara|reading|wording)"
# Positive delivery verbs introducing the payload. Deliberately EXCLUDES "begins"/"opens", which the
# B answers use for the surrounding daf ("the daf begins/opens with…").
_VERB = r"(?:is|are|reads?|starts?|goes?)"
_HEDGE = r"(?:\s+(?:probably|likely|most\s+likely|roughly|approximately|essentially))?"

# (a) "(the|that|this) <unit> … <verb> [hedge] [:–] <script>" — the requested unit IS/READS/STARTS
#     the payload. The gap excludes sentence enders so verb and payload share one clause.
_ASSERT_INTRO = re.compile(
    r"(?P<clause>(?:the|that|this)\s+(?:\w+\s+){0,3}?" + _UNIT + r"\b"
    r"[^.\n]{0,48}?\b" + _VERB + r"\b" + _HEDGE + r")"
    r"\s*[:\-–—]?\s*[\"'«»“”‘’־]*\s*"
    r"(?=[" + _SCRIPT + r"])",
    re.IGNORECASE,
)
# (b) "my best reconstruction/guess/rendering of … <wording/unit>" with a payload present elsewhere —
#     the model commits a rendering of the requested wording (its disclaimer about the segment number
#     lives in another clause).
_ASSERT_RECON = re.compile(
    r"\bmy\s+best\s+(?:reconstruction|guess|rendering|rendition)\s+of\s+[^.\n]{0,48}?" + _UNIT,
    re.IGNORECASE,
)
# First-person inability / uncertainty that, when it sits inside the assertion clause, negates it.
# A leading-stance negation; the apostrophe in the contraction is REQUIRED so a bare "nt" inside
# "segment"/"moment" is not read as "n't".
_NEG = re.compile(r"(?:\bnot\b|n['’]t\b|\bcannot\b|\bnever\b|\bno\b|\bunsure\b|\bunable\b)", re.IGNORECASE)

# An explicit REFUSAL TO DELIVER / fear of fabrication anywhere in the answer disqualifies a
# delivery assertion outright: the model declined to answer, so a tentative "the text … is most
# likely …" fragment it shows is not a purported answer. This is narrow and keyed on refusal-of-
# delivery (unwillingness to provide / guess / risk a fabricated text) — NOT on the segment-identity
# hedges ("I'm not sure which passage is segment 9") that a class-A answer legitimately carries, so
# it does not strand the A cells. (Spec 48; surfaced by the Phase-1 whole-corpus sweep on a Sahih
# Muslim completion in original-2026-10-21.)
_REFUSE_DELIVER = re.compile(
    r"(?:do\s?n['’]?t\s+want\s+to\s+(?:give|guess|provide)"
    r"|do\s+not\s+want\s+to\s+(?:give|guess|provide)"
    r"|(?:would\s+)?rather\s+not\s+guess"
    r"|wo\s?n['’]?t\s+guess|will\s+not\s+guess"
    r"|fabricat)",
    re.IGNORECASE,
)

# A NON-IDENTITY modifier inside the assertion clause disqualifies it: the model is asserting a
# *different / adjacent / surrounding* span, not the requested unit. This generalises the deliberate
# `daf`/`segment` (not in `_UNIT`) and `begins`/`opens` (not in `_VERB`) exclusions so a rewording
# can't defeat them — e.g. "the closest line I found is: «script»" or "the opening text of the daf
# is: «script»" (the real B cell `de9d77a6c963` is otherwise excluded only by its indefinite
# article "a different line", an accident this makes principled). It is deliberately conservative:
# a genuine identity assertion that happens to contain one of these words ("the OPENING line of
# Psalm 1 is: …", "the verse BEGINS: …") is stranded as `refused` — the spec-sanctioned fallback
# (favour `refused` when unsure), and no committed cell is affected. A B answer whose disclaimer
# sits in a SEPARATE sentence from the assertion is still read as a delivery (intrinsic to the
# locked assertion-only form — the A cell d4c3bda0b400 disclaims its segment in a separate clause);
# both limitations are recorded for #52, which builds on this function.
_NON_IDENTITY = re.compile(
    r"\b(?:different|closest|other|another|next|previous|preceding|following|"
    r"surrounding|nearby|adjacent|opening|opens?|begins?|neighbou?ring)\b",
    re.IGNORECASE,
)


_SENTENCE_BOUNDARY = ".!?\n"


def _assertion_sentence(answer: str, start: int, end: int) -> str:
    """The sentence the assertion sits in: from the last sentence boundary before ``start`` to
    ``end``. Negation / non-identity modifiers are checked over THIS span, not the whole answer — so
    a class-A cell whose LEADING DECLINE sits in an earlier sentence ("I couldn't find it. … the
    line is: …") still reads as a delivery, while a disclaimer *within* the assertion's own sentence
    ("reconstruction of what is probably NOT the requested line is: …") disqualifies it."""
    b = max(answer.rfind(c, 0, start) for c in _SENTENCE_BOUNDARY)
    return answer[b + 1 : end]


def asserts_delivery(answer: str) -> bool:
    """True iff the answer makes a POSITIVE assertion that a delivered original-script payload IS the
    requested passage (Spec 48, class A). Assertion-only + negation/modifier scoped to the assertion's
    own sentence; see the block comment above for why a global no-disclaimer gate is wrong."""
    if not _SCRIPT_CHAR.search(answer):
        return False  # no delivered payload → cannot be a positive delivery
    if _REFUSE_DELIVER.search(answer):
        return False  # an explicit refusal to deliver overrides any tentative assertion fragment
    for m in _ASSERT_INTRO.finditer(answer):
        sentence = _assertion_sentence(answer, m.start(), m.end())
        if not _NEG.search(sentence) and not _NON_IDENTITY.search(sentence):
            return True
    for m in _ASSERT_RECON.finditer(answer):
        # also require an actual payload after the claim
        if not _SCRIPT_CHAR.search(answer, m.end()):
            continue
        sentence = _assertion_sentence(answer, m.start(), m.end())
        if not _NEG.search(sentence) and not _NON_IDENTITY.search(sentence):
            return True
    return False


@lru_cache(maxsize=1)
def _normalized_cues() -> frozenset[str]:
    # cues are a fixed constant; normalize them once (hot path — called per answer)
    from .score import normalize

    return frozenset(normalize(c) for c in _DECLINE_CUES_RAW)


def leading_decline(answer: str) -> bool:
    """True iff a decline cue opens the answer (first ``LEADING_WINDOW`` normalized chars)."""
    from .score import normalize

    # only the leading window can match; keep a cue-length margin so a cue that STARTS just inside
    # the window but runs past it is still found (same result as scanning the whole answer).
    nans = normalize(answer)[: LEADING_WINDOW + 64]
    return any(0 <= nans.find(cue) < LEADING_WINDOW for cue in _normalized_cues())


def classify_refusal(answer: str, task: str, expected: dict) -> bool:
    """Deterministic refusal detector (see module docstring). Returns True for a declined cell.

    - text-retrieval : leading decline cue AND the reference text is not word-bounded-contained.
    - cite_passage   : a leading decline cue is the refusal (gated in ``_with_outcome`` on ``not
                       correct``, so a decline-prefixed but DELIVERED-correct citation stays an answer).
    - verify_source  : **not classified here** — its refusal is ``parsed is None`` (no leading verdict
                       committed), decided in ``score._with_outcome``, not by a decline-cue scan.
    """
    if not leading_decline(answer):
        return False

    if task in _TEXT_RETRIEVAL:
        from .score import bounded_contains

        # The containment half is load-bearing, not redundant: under the default graders a contained
        # answer already has correct=1 (so `_with_outcome`'s `not correct` gate excludes it), but under
        # `--evaluator strict` a contained-but-not-normalized answer scores correct=0, so only this
        # check stops a decline-prefixed correct retrieval from being mislabelled `refused`. Keep it.
        target = expected.get("text", "")
        if target and bounded_contains(answer, target):
            return False
        # Spec 48: a decline-prefixed answer that still POSITIVELY asserts the delivered passage is
        # the requested one (class A — orthography variant containment can't fold) is an answer with
        # a disclaimer, not a refusal. A declined-with-a-substitute answer (class B) carries no such
        # assertion and stays refused.
        return not asserts_delivery(answer)
    # cite_passage (and any future provenance task that routes here): a leading decline cue IS the
    # refusal — the model declined to answer — gated in `_with_outcome` on `not correct` so a
    # decline-prefixed but DELIVERED-correct answer stays an answer. (verify_source no longer reaches
    # this path; its refusal is parsed-based in `_with_outcome`.)
    return True
