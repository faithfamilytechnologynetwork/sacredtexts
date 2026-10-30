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

This module is deliberately thin: the primitives (``normalize``, ``fold_aware_contains``,
``parse_yes_no``) live in ``score.py`` and are imported lazily so there is no import cycle (``score``
imports this inside ``score_answer``). ``classify_refusal`` credits a delivered Imla'i-orthography
variant via ``fold_aware_contains`` (Spec 52), the same strict-superset containment the headline uses.
"""

from __future__ import annotations

import re
import unicodedata
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

# A delivered scripture payload is a run of text in the REFERENCE'S OWN script — derived per question
# from the expected text (`asserts_delivery(answer, reference)`), NOT a hardcoded allowlist. This is
# the arch invariant ("traditions are drop-in data; core code must not need per-script edits", cf.
# arch-critical / the #50 Gurmukhi gap): a new tradition in any script — Latin (KJV, LDS), Gurmukhi,
# Cyrillic, … — is recognised with zero code change, because the target script comes from the
# question's reference and `unicodedata` names each character's script family. A positive delivery
# must introduce text in that script (so for a Hebrew/Arabic reference an English-only gloss is not a
# delivery, and delivery *volume* is not the signal), AND carry a positive assertion frame.


def _script_families(text: str) -> frozenset[str]:
    """The Unicode script families present among a string's LETTERS, from ``unicodedata`` — e.g.
    ``{"HEBREW"}``, ``{"ARABIC"}``, ``{"GREEK"}``, ``{"LATIN"}``, ``{"GURMUKHI"}``. Allowlist-free, so
    a new tradition needs no code edit. Digits, combining marks, punctuation and whitespace do not
    contribute (only ``str.isalpha`` characters), so a reference's script is its letters' script."""
    fams: set[str] = set()
    for ch in text:
        if not ch.isalpha():
            continue
        if ch.isascii():
            fams.add("LATIN")
            continue
        try:
            fams.add(unicodedata.name(ch).split(" ", 1)[0])
        except ValueError:
            continue
    return frozenset(fams)


def _payload_pos(answer: str, start: int, families: frozenset[str]) -> int | None:
    """Index of the first letter at/after ``start`` whose script family is in ``families`` — the first
    delivered-payload character in the reference's own script; ``None`` if there is none. ASCII letters
    are Latin, so they short-circuit (qualify iff the reference is Latin) without a ``unicodedata``
    lookup; only non-ASCII letters are named."""
    if not families:
        return None
    latin = "LATIN" in families
    for i in range(start, len(answer)):
        ch = answer[i]
        if not ch.isalpha():
            continue
        if ch.isascii():
            if latin:
                return i
            continue
        try:
            if unicodedata.name(ch).split(" ", 1)[0] in families:
                return i
        except ValueError:
            continue
    return None


# Characters that INTRODUCE a delivered payload: a colon/dash or an opening quote.
_INTRODUCER = ":-–—\"'«»“”‘’"


def _introduced(answer: str, pos: int) -> bool:
    """True iff the payload at ``pos`` is immediately preceded (ignoring whitespace) by a delivery
    INTRODUCER — a colon/dash or an opening quote. Required only for a **same-script-as-prose
    (Latin/ASCII) payload**: there is no script shift to mark "here is the delivered text", so a bare
    "the line is about…" / "the text is also available…" is continuation prose, not a delivery, unless
    an explicit introducer sets the passage off ("the verse reads: For God so loved…"). A non-Latin
    payload needs no introducer — the script shift itself is the signal."""
    j = pos - 1
    while j >= 0 and answer[j].isspace():
        j -= 1
    return j >= 0 and answer[j] in _INTRODUCER


# Nouns a positive assertion is ABOUT: the requested unit itself. Deliberately EXCLUDES "segment",
# "daf", "page" — the B answers describe *those* ("the daf begins with…", "which part is segment 3"),
# not the requested line.
_UNIT = r"(?:line|text|verse|passage|baraita|baraisa|mishnah|mishna|gemara|reading|wording)"
# Positive delivery verbs introducing the payload. Deliberately EXCLUDES "begins"/"opens", which the
# B answers use for the surrounding daf ("the daf begins/opens with…").
_VERB = r"(?:is|are|reads?|starts?|goes?)"
_HEDGE = r"(?:\s+(?:probably|likely|most\s+likely|roughly|approximately|essentially))?"

# (a) "(the|that|this) <unit> … <verb> [hedge] [:–]" — the requested unit IS/READS/STARTS the
#     payload. The frame ends after the optional colon/quotes; the delivered payload (in the
#     reference's own script) is located separately, so detection is script-neutral. The gap excludes
#     sentence enders so verb and the delivered payload share one clause.
_ASSERT_INTRO = re.compile(
    r"(?:the|that|this)\s+(?:\w+\s+){0,3}?" + _UNIT + r"\b"
    r"[^.\n]{0,48}?\b" + _VERB + r"\b" + _HEDGE +
    r"\s*[:\-–—]?\s*[\"'«»“”‘’־]*\s*",
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
# (favour `refused` when unsure), and no committed cell is affected. The disqualifier window runs
# from the assertion frame THROUGH the payload's sentence (`_guard_span`), so a disclaimer between
# the claim and a later payload ("…is not reliable; the adjacent text is: <payload>") OR trailing it
# within the same sentence ("the line is: <payload>, but that is a different line") both disqualify
# (codex + architect PR review). The remaining limitation: a disclaimer in a SEPARATE sentence —
# before the frame's sentence or after the payload's — is not consulted (intrinsic to the sentence
# scoping that lets A cell d4c3bda0b400 decline in a prior sentence and still deliver); recorded for
# #52, which builds on this function.
_NON_IDENTITY = re.compile(
    r"\b(?:different|closest|other|another|next|previous|preceding|following|"
    r"surrounding|nearby|adjacent|opening|opens?|begins?|neighbou?ring)\b",
    re.IGNORECASE,
)


_SENTENCE_BOUNDARY = ".!?\n"


def _guard_span(answer: str, frame_start: int, payload_pos: int) -> str:
    """The span over which negation / non-identity disqualifiers are checked: from the sentence
    boundary before the assertion frame THROUGH the end of the payload's sentence. This covers a
    disqualifier in the claim's own clause, one sitting BETWEEN the claim and a later payload
    ("…is not reliable; the adjacent text is: <payload>"), and one TRAILING the payload within its
    sentence ("the line is: <payload>, but that is a different line") — while still excluding an
    earlier leading-decline sentence, so a class-A cell that declines in a prior sentence and then
    delivers still reads as a delivery."""
    start = max(answer.rfind(c, 0, frame_start) for c in _SENTENCE_BOUNDARY) + 1
    ends = [e for e in (answer.find(c, payload_pos) for c in _SENTENCE_BOUNDARY) if e != -1]
    end = min(ends) if ends else len(answer)
    return answer[start:end]


def asserts_delivery(answer: str, reference: str) -> bool:
    """True iff the answer makes a POSITIVE assertion that a delivered payload IN THE REFERENCE'S OWN
    SCRIPT is the requested passage (Spec 48, class A). Assertion-only; the target script is derived
    from ``reference`` (no allowlist — a new tradition in any script is handled with no code edit);
    negation / non-identity disqualifiers are checked from the assertion frame through the payload's
    sentence. See the block comments for why a global no-disclaimer gate is wrong."""
    families = _script_families(reference)
    if not families:
        return False  # no reference script to deliver in → cannot judge a positive delivery
    if _REFUSE_DELIVER.search(answer):
        return False  # an explicit refusal to deliver overrides any tentative assertion fragment
    # INTRO requires the payload in the frame's OWN sentence (adjacent, like the old lookahead); RECON
    # commits to a payload that may sit in a later clause, so it is allowed elsewhere in the answer.
    for frame, adjacent in ((_ASSERT_INTRO, True), (_ASSERT_RECON, False)):
        for m in frame.finditer(answer):
            p = _payload_pos(answer, m.end(), families)
            if p is None:
                continue  # the assertion commits to no payload in the reference's script
            if answer[p].isascii() and not _introduced(answer, p):
                continue  # a Latin/ASCII payload (no script shift) needs an explicit introducer,
                # else "the line is about…" / "the text is also available…" is continuation prose
            if adjacent and any(c.isalpha() for c in answer[m.end() : p]):
                continue  # INTRO: the payload must IMMEDIATELY follow the frame (only spaces /
                # punctuation / quotes between) — as the old script lookahead required. Intervening
                # WORDS mean the delivered payload is not what the frame introduces (e.g. "…segment 7
                # is probably either X or the follow-up question, «script»" — a B description, not a
                # delivery of the requested line).
            span = _guard_span(answer, m.start(), p)
            if not _NEG.search(span) and not _NON_IDENTITY.search(span):
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
        from .score import fold_aware_contains

        # The containment half is load-bearing, not redundant: under the default graders a contained
        # answer already has correct=1 (so `_with_outcome`'s `not correct` gate excludes it), but under
        # `--evaluator strict` a contained-but-not-normalized answer scores correct=0, so only this
        # check stops a decline-prefixed correct retrieval from being mislabelled `refused`. Keep it.
        # Spec 52: fold_aware_contains (strict superset) so a delivered Imla'i-orthography variant is
        # likewise recognised as an answer, not a refusal.
        target = expected.get("text", "")
        if target and fold_aware_contains(answer, target):
            return False
        # Spec 48: a decline-prefixed answer that still POSITIVELY asserts the delivered passage is
        # the requested one (class A — orthography variant containment can't fold) is an answer with
        # a disclaimer, not a refusal. A declined-with-a-substitute answer (class B) carries no such
        # assertion and stays refused. The reference text supplies the target script (no allowlist).
        return not asserts_delivery(answer, target)
    # cite_passage (and any future provenance task that routes here): a leading decline cue IS the
    # refusal — the model declined to answer — gated in `_with_outcome` on `not correct` so a
    # decline-prefixed but DELIVERED-correct answer stays an answer. (verify_source no longer reaches
    # this path; its refusal is parsed-based in `_with_outcome`.)
    return True
