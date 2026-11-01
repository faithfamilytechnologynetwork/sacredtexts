"""Scoring: per answer, the metrics the SELECTED graders emit plus always-on diagnostics.
The default graders are ``strict`` + ``containment`` (Spec 15: ``normalized OR contains_reference``).

Metrics emitted per answer:

- ``exact``       raw string equality with the expected text (0/1)
- ``normalized``  equality after normalisation: unicode quotes/dashes folded,
                  Arabic/Hebrew combining marks + annotation symbols removed and
                  alef/maqaf variants folded (so vocalised ↔ unvocalised scripture
                  matches), case-folded, punctuation stripped, whitespace collapsed
                  (0/1) — see ``strip_script_marks``. Uthmani/Imla'i orthography is
                  NOT folded here (Spec 52); it is credited only by
                  ``fold_aware_contains``.
- ``token_f1``    bag-of-words F1 between normalised answer and expected text
                  (0..1). A vowel sign or Latin accent is part of the word, so
                  dropping it misses that word. This does not decide ``correct``.
- ``token_f1_base`` the same F1 after vowel signs and Latin accents are removed.
                  High here and low on ``token_f1`` means the words are right and
                  the marks are not. Also not the headline.
- ``contains_reference``  (retrieve_quote / complete_unit ONLY) the normalised reference
                  appears word-bounded inside the normalised answer (0/1) — catches a
                  correct-but-wrapped retrieval (bracketed quote + a citation/caveat) that
                  strict ``normalized`` scores 0. A strict superset of ``normalized``.
- ``correct``     the per-task headline judgment (see below)
- ``outcome``     (Spec 15) ``correct`` / ``incorrect`` / ``refused`` — a declined answer is
                  ``refused`` (``correct`` forced 0) and EXCLUDED from accuracy; see
                  ``_with_outcome`` and ``outcomes.classify_refusal``. Accuracy is then
                  ``correct/(correct+incorrect)`` and ``score_file`` reports ``coverage`` beside it.

For the text-retrieval tasks the reported sub-metrics and the headline are set by the SELECTED
graders (``graders.py``, chosen via ``score --evaluator``; default ``strict`` + ``containment``).

Per-task headline rule (the spec's contract — designed to resist evasive answers so
that containment alone cannot game provenance honesty, within the SCOPE noted below):

- retrieve_quote / complete_unit : OR of the selected graders' verdicts — default
                                   ``normalized`` OR ``contains_reference`` (Spec 15: a
                                   verbatim quote wrapped in brackets/notes IS a correct
                                   retrieval; exact + token-F1 reported alongside).
                                   Containment is confined to these two text-retrieval
                                   tasks — the provenance tasks below never use it.
- verify_source                  : the parsed **leading-stance** Yes/No equals expected
                                   (``parse_yes_no``: Yes/No must be the leading token, so a
                                   negation-evasion like "there is no way to verify this" is
                                   NOT read as "no") — closes the #23 PAPER GATE
- cite_passage                   : the SINGLE extracted citation EQUALS ground truth
                                   (boundary-aware, not containment); a multi-candidate
                                   hedge scores 0, a repeated correct citation does not

(``identify_version`` and ``identify_source`` were retired in Spec 26: the question set is
original-language-only, so there are never ≥2 editions of one work for ``identify_version``, and
``cite_passage`` subsumes ``identify_source``.)

SCOPE / known gaps (tracked for the Spec 2 scoring-contract revision):
- the citation anti-hedge counts only FORMALLY-SHAPED citation candidates, so a
  PROSE hedge ("it could be Jude 1:3, or perhaps chapter 1 verse 4") is not caught.
- ``cite_passage`` over Arabic ground truth: the span extractors expect a Latin-script leading
  word and ``normalize()`` does not fold Arabic-Indic digits — evaluated in the Spec 26 run.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


class ScoreError(Exception):
    pass


_PUNCT_RE = re.compile(r"[^\w\s]", re.UNICODE)
_WS_RE = re.compile(r"\s+")

# The RTL Unicode blocks (U+0590–U+08FF is Hebrew + Arabic + their extensions — and also
# Syriac/Thaana/N'Ko/Samaritan/Mandaic, whose marks we strip too; harmless for this
# benchmark's Arabic/Hebrew corpora; plus U+FB1D–U+FB4F Hebrew/Arabic presentation forms).
# Combining marks (category Mn) ANYWHERE in these blocks are deleted — a strict superset
# of the QUL mark set, so a search-on answer carrying marks from another Uthmani
# digitization (U+0617–U+061A, U+0656–U+065F, Arabic Extended-A U+08D3–U+08FF) is still
# folded, not split mid-word. The ranges are script-scoped, so Latin combining marks
# (U+0300–U+036F) are untouched and Latin output is byte-for-byte unchanged.
#
# NOT handled here (deliberately): invisible bidi/joiner/BOM formatting from the General
# Punctuation block (U+200C–U+200F, U+FEFF, U+00AD) that can ride along in web-fetched RTL
# answers. Deleting them globally would change the Latin path (soft hyphen currently folds
# to a space, which the committed first-run relies on), breaking the Latin-invariance
# contract — the re-score regression guard enforces this. They are a Phase-3 answer-review
# watch item (a split answer is visible there), not a Phase-1 concern (no committed corpus
# text carries them).
_SCRIPT_BLOCKS = ((0x0590, 0x08FF), (0xFB1D, 0xFB4F))
# Editorial code points in those blocks that are NOT category Mn and so must be deleted
# explicitly: the Arabic tatweel (Lm) and the Qur'anic annotation block U+06D6–U+06ED,
# which mixes Mn marks with the rub-el-hizb / sajdah symbols (So) and small waw/yeh (Lm).
_SCRIPT_EDITORIAL = frozenset("ـ") | frozenset(chr(c) for c in range(0x06D6, 0x06EE))


def _in_script_blocks(ch: str) -> bool:
    o = ord(ch)
    return any(lo <= o <= hi for lo, hi in _SCRIPT_BLOCKS)


def _is_greek_base(ch: str) -> bool:
    o = ord(ch)
    return 0x0370 <= o <= 0x03FF or 0x1F00 <= o <= 0x1FFF


def strip_script_marks(text: str) -> str:
    """Fold Arabic/Hebrew letter variants and remove their combining marks so quote
    scoring compares bare consonantal text. Greek accents and breathings are removed
    too, so they do not become word breaks. Applied to BOTH the answer and the
    expected text, so the direction of vocalisation does not matter."""
    text = text.replace("ٱ", "ا")  # Arabic alef-wasla -> bare alef (atomic;
    #                                           alef-madda/hamza fold via NFKD + marks)
    text = text.replace("־", " ")  # Hebrew maqaf -> word boundary (NOT deleted:
    #                                      it joins words, so it must stay a separator)
    # Combining marks in the RTL blocks are deleted. Greek accents live in the
    # combining block, so they are deleted only when they sit on a Greek letter.
    # That leaves Latin combining marks on the path they already had.
    out = []
    prev_greek = False
    for ch in text:
        drop_rtl = _in_script_blocks(ch) and (unicodedata.category(ch) == "Mn" or ch in _SCRIPT_EDITORIAL)
        drop_greek = prev_greek and unicodedata.category(ch) == "Mn"
        if drop_rtl or drop_greek:
            continue
        out.append(ch)
        if unicodedata.category(ch) != "Mn":
            prev_greek = _is_greek_base(ch)
    return "".join(out)

# Fixed sub-metrics for the NON-graded tasks. The text-retrieval tasks (retrieve_quote /
# complete_unit) derive their submetric set from the selected graders (see graders.submetrics_for);
# verify_source and cite_passage carry no fixed submetrics. (identify_version / identify_source were
# retired in Spec 26, so this is now empty — kept for the per-task dispatch and the doc pointer-guard.)
_SUBMETRICS: dict[str, tuple[str, ...]] = {}


def normalize(text: str) -> str:
    """The shared normaliser (generation, scoring, audit-adjacent). Byte-stable by contract —
    its Arabic behaviour must NOT change (Spec 52 keeps the orthography fold out of this path, in
    ``score_normalize``). Thin delegate to ``_normalize`` so it cannot drift from it."""
    return _normalize(text, fold=False)


def _normalize(text: str, *, fold: bool, plene: bool = False) -> str:
    """Shared normalisation pipeline — ONE implementation so the entry points cannot drift (iter-2/3).
    ``fold=False`` keeps the historical Arabic and Hebrew behaviour. Latin diacritics
    stay on the letter (café, Yoḥanan). Gurmukhi, Devanagari, and romanized Pali keep
    their vowel signs (issue #50).
    ``fold=True`` adds the
    symmetric Arabic folds (ء→ا, bare ى→ي) after NFKD + quote/dash and BEFORE the Mn-mark deletion.
    ``plene=True`` (only with ``fold``) additionally MATERIALISES every long ā — the ``ىٰ`` digraph and
    the lone dagger-alif → full alef — instead of letting the mark pass delete the dagger; used for
    the direction-independent answer form in ``fold_aware_contains``."""
    text = unicodedata.normalize("NFKD", text)
    text = text.replace("‘", "'").replace("’", "'")
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("–", "-").replace("—", "-")
    if plene:  # long ā → alef, BEFORE the mark pass that would otherwise delete the dagger
        text = _materialise_long_alif(text)
    if fold:
        text = fold_arabic_orthography(text)
    text = strip_script_marks(text)  # Arabic/Hebrew marks BEFORE the punctuation pass,
    #                                  so they are removed, not turned into word splits
    # NFKD splits café, Yoḥanan, Ismāʿīl, and dhammā into a letter plus a mark.
    # Glue every Latin letter back to the marks that follow it, then the
    # punctuation pass cannot turn the accent into a word break. Arabic and
    # Hebrew marks are already gone, so this does not reassemble those.
    text = _recompose_latin_marks(text.casefold())
    text = _fold_punct(text)
    return _WS_RE.sub(" ", text).strip()


def _is_latin_base(ch: str) -> bool:
    o = ord(ch)
    return unicodedata.category(ch).startswith("L") and (
        0x0041 <= o <= 0x024F or 0x1E00 <= o <= 0x1EFF
    )


def _is_latin_mark(ch: str) -> bool:
    """A combining mark NFKD splits off a Latin letter (macron, dot below, acute)."""
    o = ord(ch)
    return unicodedata.category(ch) == "Mn" and (
        0x0300 <= o <= 0x036F or 0x1AB0 <= o <= 0x1AFF or 0x1DC0 <= o <= 0x1DFF
    )


def _recompose_latin_marks(text: str) -> str:
    """Put a diacritic back on its Latin letter so the word stays one word."""
    out: list[str] = []
    i, n = 0, len(text)
    while i < n:
        j = i + 1
        if _is_latin_base(text[i]):
            while j < n and _is_latin_mark(text[j]):
                j += 1
        if j > i + 1:
            out.append(unicodedata.normalize("NFC", text[i:j]))
            i = j
        else:
            out.append(text[i])
            i += 1
    return "".join(out)


def _is_indic_mark(ch: str) -> bool:
    """A Gurmukhi or Devanagari vowel sign, virama, or nasal mark. These are
    category M, so ``\\w`` does not count them, and the punctuation pass would
    otherwise split the word. Danda (category P) stays punctuation."""
    o = ord(ch)
    if not (0x0900 <= o <= 0x097F or 0x0A00 <= o <= 0x0A7F):
        return False
    return unicodedata.category(ch).startswith("M")


# Zero-width joiner and non-joiner sit inside a conjunct (बुद्‍ध्या) and are not
# letters. Turning them into a space splits the word. The committed runs contain
# neither, so deleting them does not move a stored score. Soft hyphen stays a space.
_INDIC_JOINERS = frozenset("\u200c\u200d")


def _fold_punct(text: str) -> str:
    out: list[str] = []
    for ch in text:
        if ch in _INDIC_JOINERS:
            continue
        if _is_indic_mark(ch):
            out.append(ch)
        elif _PUNCT_RE.match(ch):
            out.append(" ")
        else:
            out.append(ch)
    return "".join(out)


# --- Arabic orthography fold (Spec 52) ---------------------------------------------------------
# Uthmani (QUL corpus) and standard Imla'i spell the SAME Qur'anic word differently. NFKD + mark
# deletion already fold alif-madda آ, hamza-seats أ/إ/ؤ/ئ, and wasl ٱ (see the test suite). The
# residual gaps and HOW each is handled:
#   - alef-maqsura ى (U+0649) ↔ dotted ya ي    — a SYMMETRIC letter fold (both sides), monotonic;
#   - standalone hamza ء (U+0621, not NFKD-decomposed) ↔ ا — SYMMETRIC (equates أَرَءَيْتُمْ↔أَرَأَيْتُمْ;
#                                    "drop" is asymmetric and fails that pair);
#   - the long-ā written as a dagger-alif ـٰ (U+0670) or the ىٰ digraph — this is the HARD one and is
#     NOT a symmetric fold. Standard Imla'i writes the long ā as a full alef for the plene class
#     (ٱلْكِتَٰبِ→الكتاب, سُبْحَٰنَ→سبحان) but OMITS it for the DEFECTIVE-SPELLING (رسم ناقص) class
#     (هَٰذَا→هذا, ذَٰلِكَ→ذلك, ٱلرَّحْمَٰنِ→الرحمن, لَٰكِن→لكن). Which class a word is in is LEXICAL, not
#     positional — so no context-free `dagger→ا` works: forcing the alef un-credits هذا/ذلك/الرحمن
#     (today `normalize()` deletes the dagger, so those match), while deleting it un-credits the
#     plene class. The ONLY correct treatment is to make the long-ā alef OPTIONAL, which a canonical
#     string cannot express — so it lives in the CONTAINMENT predicate as `ا?` (see below), and the
#     equality submetrics keep today's dagger deletion. (This is why the earlier `dagger→ا` fold was
#     abandoned — Spec 52 review, architect-approved 2026-10-29.)
#
# DESIGN: the shared `normalize()` and the equality submetrics (`exact`/`normalized`/`token_f1`) are
# UNCHANGED. ALL orthographic flexibility lives in `fold_aware_contains`, which is a strict SUPERSET
# of today's `bounded_contains` — so it can only ADD credit, never remove it; `normalized=1 ⇒
# contains=1` is preserved, non-Arabic and all similarity submetrics are frozen, and generation's
# `normalize()` (hence the question-set digest) and the copyright audit are untouched.
#
# ACCEPTED COLLISION RESIDUE (known limitation, architect-approved). The fold rules merge a few rare
# distinct-word minimal pairs sharing a consonantal skeleton (10 QUL buckets):
#   - hamza (ء→ا): سواء/سوء, جزاء/جزء, وراء/ورء, ملأ/ملء, شىء/شيـٔا, برىء/بريـٔا
#   - maqsura (ى→ي): نبى/نبّئ, قرى/قرئ, أمرى/امرئ
#   - optional-long-ā (plene branch only): رأىٰ "he saw" / رءا
# The no-wrong-credit gate is at scoring granularity (every rebaselined cell hand-verified; see
# `test_arabic_orthography_fold.py`, which pins all 10 over BOTH answer canonicalisations, and the
# Spec 52 review). Verse-length references make a one-word ambiguity essentially never flip a cell.
_DAGGER_ALEF = "ٰ"   # ARABIC LETTER SUPERSCRIPT ALEF (category Mn) — the long-ā diacritic
_ALEF_MAQSURA = "ى"  # ARABIC LETTER ALEF MAKSURA
_YA = "ي"            # ARABIC LETTER YEH
_ALEF = "ا"          # ARABIC LETTER ALEF
_HAMZA = "ء"         # ARABIC LETTER HAMZA (standalone)
_WASL = "ٱ"          # ARABIC LETTER ALEF WASLA


def _dagger_after_maqsura(text: str, i: int) -> int | None:
    """Index of the dagger that closes a ``ىٰ`` digraph at ``text[i]``, or ``None``.

    Tatweel and combining marks between the alef maqsura and the dagger still count.
    NFKD sorts fatha (combining class 30) before the dagger (class 35), so a typed
    ``ىَٰ`` arrives as ``ى`` + fatha + dagger. An adjacent-only check folds that ``ى``
    to ``ي`` and the long ā is lost.
    """
    if i >= len(text) or text[i] != _ALEF_MAQSURA:
        return None
    j = i + 1
    while j < len(text) and text[j] != _DAGGER_ALEF and (
        text[j] == "ـ" or unicodedata.combining(text[j])
    ):
        j += 1
    if j < len(text) and text[j] == _DAGGER_ALEF:
        return j
    return None


def _materialise_long_alif(text: str) -> str:
    """Rewrite every long-ā dagger, including a ``ىٰ`` digraph with marks or tatweel
    inside it, to a full alef. Marks inside the digraph are consumed with it."""
    out: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        end = _dagger_after_maqsura(text, i)
        if end is not None:
            out.append(_ALEF)
            i = end + 1
            continue
        out.append(_ALEF if text[i] == _DAGGER_ALEF else text[i])
        i += 1
    return "".join(out)


def fold_arabic_orthography(text: str) -> str:
    """The SYMMETRIC Arabic letter folds (Spec 52), applied to both answer and expected: standalone
    hamza ء → alef ا, and a BARE alef-maqsura ى → dotted ya ي. A ى that carries a dagger (the ``ىٰ``
    long-ā digraph, even with a vowel mark or tatweel between them) is left alone — folding it to ya
    would collide the long-ā form with a genuine ``…ay…`` word (ءَاتَىٰنَا "He gave us" vs ءَاتَيْنَا
    "we gave"); the digraph's long ā is instead handled, optionally, in ``fold_aware_contains``.
    Expects NFKD-normalised input, runs BEFORE the Mn-mark deletion (which removes the dagger as
    before). Arabic-only — Latin byte-for-byte unchanged.

    NOT the same as ``probes.fold_arabic_letters``: that is a LOOSER, PROBE-ONLY fold (it also
    collapses ``آ → ا`` and ``ة → ه`` outright) used for diagnostics, never for a scored headline —
    keep the two deliberately distinct."""
    text = text.replace(_HAMZA, _ALEF)
    out: list[str] = []
    i = 0
    while i < len(text):
        if text[i] == _ALEF_MAQSURA and _dagger_after_maqsura(text, i) is None:
            out.append(_YA)
        else:
            out.append(text[i])
        i += 1
    return "".join(out)


def score_normalize(text: str) -> str:
    """``normalize()`` plus the SYMMETRIC Arabic letter folds (ى→ي, ء→ا), interleaved after NFKD and
    before the mark pass. Used only as the answer-side normalisation inside ``fold_aware_contains``
    (and to build its reference pattern); the shared ``normalize()`` — and every equality submetric —
    stays untouched (Spec 52)."""
    return _normalize(text, fold=True)


def _is_arabic_letter(c: str) -> bool:
    """An Arabic-script LETTER (category L) — the base/Supplement/Extended blocks and presentation
    forms, excluding Arabic-Indic DIGITS (category Nd) so numeric separators are never collapsed."""
    o = ord(c)
    return (
        0x0600 <= o <= 0x06FF or 0x0750 <= o <= 0x077F
        or 0x08A0 <= o <= 0x08FF or 0xFB50 <= o <= 0xFEFF
    ) and unicodedata.category(c).startswith("L")


def _fold_containment_pattern(expected: str) -> str:
    """Build a word-bounded containment regex from an Arabic reference (Spec 52) that:
    (a) makes the long-ā alef OPTIONAL (``ا?``) at each dagger-alif / ``ىٰ`` digraph position — so a
        plene (ٱلْكِتَٰبِ→الكتاب), defective (هَٰذَا→هذا) or Uthmani answer all match;
    (b) applies the symmetric folds (ى→ي, ء→ا, wasl ٱ→ا), drops marks/editorial;
    (c) allows optional ``\\s*`` ONLY at a long-ā join boundary (a gap abutting an optional-long-ā
        "AA" atom), so the attested Uthmani one-word ↔ Imla'i two-word compound (يَـٰبُنَىَّ ↔ يَا بُنَيَّ)
        matches either direction — while elsewhere a reference space stays REQUIRED and adjacent
        letters stay CONTIGUOUS, so a multiword reference does NOT match a distinct single word
        (منشر ≠ ``من شر``, ``ك تب`` ≠ كتب) and a space next to a DIGIT stays required (``١ ٣`` ≠ ``١٣``);
    (d) is anchored ``(?<!\\w)…(?!\\w)`` so it stays a bounded containment (no sub-word credit)."""
    s = unicodedata.normalize("NFKD", expected)
    s = s.replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')
    s = s.replace("–", "-").replace("—", "-")
    # Walk into atoms: a literal folded char, a kept space, or the optional-long-ā marker "AA".
    atoms: list[str] = []
    i, n = 0, len(s)
    while i < n:
        ch = s[i]
        end = _dagger_after_maqsura(s, i)
        if end is not None:
            atoms.append("AA"); i = end + 1; continue     # ىٰ digraph → optional long ā
        if ch == _DAGGER_ALEF:
            atoms.append("AA"); i += 1; continue           # lone dagger → optional long ā
        if ch in (_HAMZA, _WASL):
            atoms.append(_ALEF); i += 1; continue           # symmetric → alef
        if ch == _ALEF_MAQSURA:
            atoms.append(_YA); i += 1; continue             # symmetric → ya
        if _in_script_blocks(ch) and (unicodedata.category(ch) == "Mn" or ch in _SCRIPT_EDITORIAL):
            i += 1; continue                                # drop marks/editorial
        # fold punctuation AND any whitespace (newline/tab) to a single space and casefold, mirroring
        # normalize()'s final passes incl. the _WS_RE collapse — else a `\n` in a reference compiles
        # to a required literal newline the (space-collapsed) answer can never contain.
        atoms.append(" " if (_PUNCT_RE.match(ch) or ch.isspace()) else ch.casefold())
        i += 1
    # collapse space runs; drop spaces flanked by Arabic letters / the AA marker (the compound
    # boundary); strip ends.
    def is_letterish(a: str) -> bool:
        return a == "AA" or (len(a) == 1 and _is_arabic_letter(a))
    collapsed: list[str] = []
    for a in atoms:
        if a == " " and collapsed and collapsed[-1] == " ":
            continue
        collapsed.append(a)
    while collapsed and collapsed[0] == " ":
        collapsed.pop(0)
    while collapsed and collapsed[-1] == " ":
        collapsed.pop()
    # Whitespace flexibility is CONFINED to the attested Uthmani↔Imla'i word-join: the long-ā
    # boundary (vocative يٰ.../يا ..., dagger-join يَـٰبُنَىَّ↔يَا بُنَيَّ) — i.e. a position adjacent to an
    # optional-long-ā ("AA") atom, which is the only boundary where the two orthographies attestedly
    # join-vs-split. Everywhere else a reference space stays REQUIRED and adjacent letters stay
    # CONTIGUOUS, so a multiword reference cannot match a distinct single word (منشر ≠ "من شر",
    # "ك تب" ≠ كتب) and no distinct segmentation is credited. (Spec 52 PR review, architect round-1
    # item 1 — codex segmentation over-credit.)
    def aa_join(j: int) -> bool:  # does the gap at position j abut an optional-long-ā atom?
        left = collapsed[j - 1] if j > 0 else None
        right = collapsed[j + 1] if j + 1 < len(collapsed) else None
        return left == "AA" or right == "AA"
    kept = [
        a for j, a in enumerate(collapsed)
        if not (a == " " and 0 < j < len(collapsed) - 1
                and is_letterish(collapsed[j - 1]) and is_letterish(collapsed[j + 1])
                and aa_join(j))
    ]
    parts: list[str] = []
    for j, a in enumerate(kept):
        parts.append(re.escape(_ALEF) + "?" if a == "AA" else (r"\s+" if a == " " else re.escape(a)))
        if (j + 1 < len(kept) and is_letterish(a) and is_letterish(kept[j + 1])
                and (a == "AA" or kept[j + 1] == "AA")):
            parts.append(r"\s*")           # optional space ONLY at a long-ā join boundary
    return r"(?<!\w)" + "".join(parts) + r"(?!\w)"


def _answer_plene_form(text: str) -> str:
    """The answer normalised with every long ā MATERIALISED as a full alef (``ىٰ``/dagger → ا) plus the
    symmetric folds — ``_normalize(fold=True, plene=True)``. Used alongside the default (dagger-deleted)
    ``score_normalize`` so matching is DIRECTION-INDEPENDENT: it lets an Imla'i *reference* (written
    alef) match an Uthmani *answer* (dagger), the reverse of the common case."""
    return _normalize(text, fold=True, plene=True)


def fold_aware_contains(answer: str, expected: str) -> bool:
    """Containment that credits an Uthmani↔Imla'i orthographic match (Spec 52), as a strict SUPERSET
    of ``bounded_contains``: true if the reference is already word-bounded-contained today, OR (for
    an Arabic reference) if the optional-long-ā, whitespace-flexed, word-bounded pattern built from
    the reference matches the answer. Being a superset keeps ``normalized=1 ⇒ contains=1`` and
    guarantees the fold only ADDS credit. The per-position optionality lives in the PATTERN (``ا?``
    at each REFERENCE dagger/``ىٰ``), and the answer is matched in BOTH its default (dagger-deleted)
    and plene (dagger→alef) forms — so any answer orthography (plene, defective, or mixed) matches a
    reference, in either reproduction direction, and the dual answer form is load-bearing (it credits
    answers that write a dagger where the reference wrote a full alef). LIMITATION: because the
    per-position optionality is carried by the reference's daggers, a reference that is itself written
    in MIXED Imla'i (e.g. defective ``هذا`` + plene ``الكتاب``, no daggers to mark) is NOT fully
    matched — the two global answer forms cannot reproduce a per-word mix. This never arises on the
    committed corpora (references are the corpus orthography — Uthmani for the Qur'an, carrying the
    daggers); see the Spec 52 review's residuals. SCOPE of the "only ADDS credit" guarantee: it is
    exact for the containment headline under the default graders. Under ``--evaluator strict`` the
    ``_with_outcome`` rule ``classify_refusal(...) and not correct`` means a decline-prefixed Imla'i
    delivery now folds to ``incorrect`` instead of ``refused`` (coverage ↑, accuracy ↓) — the same
    rule ``bounded_contains`` already applied, just reaching more deliveries; no committed run uses
    strict. Empty reference never matches."""
    if not normalize(expected):
        return False
    if bounded_contains(answer, expected):          # today's contract — superset floor
        return True
    if not any(_is_arabic_letter(c) for c in expected):
        return False                                 # non-Arabic refs get only today's behaviour
    pattern = _fold_containment_pattern(expected)
    return any(
        re.search(pattern, na) is not None
        for na in (score_normalize(answer), _answer_plene_form(answer))
    )


def gurmukhi_scoring_unaware() -> bool:
    """True while ``normalize()`` collapses Gurmukhi vowel signs (ਕਰਤਾ == ਕਰਤੀ) — the
    Spec 50 part-1 canary (PR #51 review): the punctuation pass turns dependent vowel
    signs into spaces, so every downstream metric on a Gurmukhi text is silently
    corrupt. Issue #50 part 2 makes ``normalize()`` keep Indic vowel signs, and the
    collect/score gates keyed on this canary open by themselves."""
    return normalize("ਕਰਤਾ") == normalize("ਕਰਤੀ")


def pali_scoring_unaware() -> bool:
    """True while ``normalize()`` folds romanized Pali diacritics (dhammā == dhamma): NFKD
    splits a diacritic off its letter and the punctuation pass turns it into a space, so
    long vowels vanish and words split (manopubbaṅgamā -> ``manopubban gama``). Issue #50
    part 2 covers this too; the gates keyed on this canary open by themselves."""
    return normalize("dhammā") == normalize("dhamma")


def devanagari_scoring_unaware() -> bool:
    """True while ``normalize()`` collapses Devanagari vowel signs (कर्ता == कर्ती): the same
    pass turns vowel signs and viramas into spaces (कर्मण्येवाधिकारस्ते ->
    ``कर मण य व ध क रस त``). Issue #50 part 2 covers this too; the gates keyed on this canary
    open by themselves."""
    return normalize("कर्ता") == normalize("कर्ती")


# language -> (display name, standardized source dir, canary) for the collect/score gates.
SCORING_GATES = {
    "pa": ("Gurmukhi", "Sikhism", gurmukhi_scoring_unaware),
    "pi": ("Pali", "Buddhism", pali_scoring_unaware),
    "sa": ("Devanagari", "Hinduism", devanagari_scoring_unaware),
}


def gated_languages() -> dict[str, tuple[str, str]]:
    """Languages ``collect`` and ``score`` must refuse now: ``{language: (name, source dir)}``."""
    return {lang: (name, source) for lang, (name, source, unaware) in SCORING_GATES.items() if unaware()}


def _f1(a: list[str], e: list[str]) -> float:
    if not a or not e:
        return 0.0
    overlap = sum((Counter(a) & Counter(e)).values())
    if overlap == 0:
        return 0.0
    precision, recall = overlap / len(a), overlap / len(e)
    return 2 * precision * recall / (precision + recall)


def token_f1(answer: str, expected: str) -> float:
    return _f1(normalize(answer).split(), normalize(expected).split())


def base_letters(text: str) -> str:
    """``normalize()`` with vowel signs and Latin accents removed.

    Greek accents and Arabic/Hebrew vowel marks are already gone. What this
    drops is the marks that distinguish a word: Pali length, Indic vowel signs,
    and English diacritics (``ḥ``, ``é``). Used only by ``token_f1_base``."""
    out: list[str] = []
    for ch in unicodedata.normalize("NFKD", normalize(text)):
        if _is_latin_mark(ch) or _is_indic_mark(ch):
            continue
        out.append(ch)
    return _WS_RE.sub(" ", "".join(out)).strip()


def token_f1_base(answer: str, expected: str) -> float:
    return _f1(base_letters(answer).split(), base_letters(expected).split())


_YES_NO_LEADING = re.compile(r"[^\w]*(yes|no)\b", re.IGNORECASE)
_SENTENCE_END = re.compile(r"[.!?\n]")
_LEADING_CHARS = 60  # the leading window: first sentence or this many chars, whichever is shorter
# leading markdown emphasis / bullets / wrapping quotes to strip before reading a verdict
_LEADING_MARKUP = re.compile(r"^[\s>*_~`\"'“”‘’•·\-–—]+")
# a bare label the prompt's "Answer Yes or No" invites ("Answer: Yes", "Verdict - No") — stripped so
# the verdict after it is leading (architect 2026-10-21). NOT a general window search: only this
# fixed label form, so "Based on my search, yes" and "There is no way to verify this" stay un-stripped.
_LABEL_PREFIX = re.compile(r"^(?:answer|verdict|response)\s*[:\-–]\s*", re.IGNORECASE)


def _leading_window(answer: str) -> str:
    """The leading segment of the RAW answer a stance may occupy: strip leading markdown/quotes/
    bullets and a bare ``Answer:``/``Verdict:``/``Response:`` label, then take the first sentence or
    the first 60 chars, whichever is shorter. Taken BEFORE ``normalize()`` (which deletes the
    sentence-ending punctuation and markup this depends on)."""
    s = _LEADING_MARKUP.sub("", answer.strip(), count=1)
    s = _LABEL_PREFIX.sub("", s, count=1)
    end = _SENTENCE_END.search(s)
    cut = min(end.start() if end else len(s), _LEADING_CHARS)
    return s[:cut]


def parse_yes_no(answer: str) -> str | None:
    """The **leading-stance** Yes/No verdict, or ``None`` (Spec 26, closes the #23 PAPER GATE).

    A verdict counts only when Yes/No is the **leading token of the leading window**
    (``_leading_window`` — first sentence / first 60 chars of the raw answer), not merely the first
    Yes/No found *anywhere*. Requiring the leading token — rather than searching the window — is what
    resists the negation-evasion #23 is about: a window *search* would still match the incidental
    ``no`` inside ``"There is no way to verify this"`` and score a false-premise ``no``-correct.

    - ``"No, that is from Sahih Muslim"`` → ``no``   (leading ``No``)
    - ``"Yes."`` → ``yes``
    - ``"There is no way to verify this... Yes"`` → ``None`` (window leads with "There"; the "no" is
      in "no way", the trailing "Yes" is outside the first sentence) — not gamed into a correct "no"
    - a non-committal / declined answer with no leading verdict → ``None`` (``score._with_outcome``
      classifies a ``None``-parse verify_source cell as ``refused``)
    """
    m = _YES_NO_LEADING.match(_leading_window(answer))
    return m.group(1).lower() if m else None


def _contains(answer: str, needle: str) -> bool:
    return normalize(needle) in normalize(answer)


def text_key(source: dict) -> tuple[str, str, str] | None:
    """The per-text key from a question's source: the ``(work, version, language)`` tuple (one text =
    one such tuple). ``None`` when any part is absent, so a malformed row never creates a phantom
    text bucket."""
    work, version, language = source.get("work"), source.get("version"), source.get("language")
    if not (work and version and language):
        return None
    return (work, version, language)


# NUL joins the (work, version, language) tuple into an UNAMBIGUOUS summary key — no field can
# contain NUL, so distinct tuples never collide (unlike a " | " join). Same convention the viewer's
# standings key uses. Split back with .split("\u0000") for display.
TEXT_KEY_SEP = "\u0000"


def _text_label_display(key: str) -> str:
    work, version, language = key.split(TEXT_KEY_SEP)
    return f"{work} ({version}, {language})"


# A citation SPAN: the numeric/para token WITH its leading work/book words
# ("John 1:1", "1 Nephi 3:7", "Taanit 2a:1", "2:255", "Rerum Novarum, para. 5"),
# so a cross-book hedge ("John 1:1, Genesis 1:1, or Micah 1:1") is three distinct
# candidates, not one. (Number-only citations, e.g. a bare hadith number, are not
# span-extracted — Arabic corpora are a follow-on; the first run is English.)
# Citation span extractors (prefix is case-insensitive so lowercase answers are
# still extracted and lowercase hedges are still counted). The extractor is chosen
# by the SHAPE of the ground-truth citation — a colon citation only counts colon
# spans, so an incidental "ASV 1901" or "Chapter 1" is not a spurious candidate.
_COLON_CITE = re.compile(r"(?:[A-Za-z0-9][^\s,:]*\s+){0,8}\d+[ab]?\s*:\s*\d+")
# the (?![Pp]ara) guard stops the greedy prefix from swallowing an earlier
# "para. N", so each paragraph citation in a hedge is its own candidate
_PARA_CITE = re.compile(r"(?:(?![Pp]ara)[A-Za-z0-9][^\s,]*,?\s+){0,8}[Pp]ara\.?\s*\d+")
# number-only (hadith "Sahih al-Bukhari 1", "Sahih Muslim 2109a"): >=1 leading word + a
# TERMINAL number that MAY carry a single a/b sub-hadith suffix (sunnah.com numbering). The
# suffix is part of the citation token, so a letter-suffixed number is a real candidate and a
# hedge over suffixed numbers ("Sahih Muslim 2109a or 3311b") is caught as multi-candidate; the
# `(?![\d:])` tail still rejects a partial number and a colon span (handled by _COLON_CITE).
_NUM_CITE = re.compile(r"(?:[A-Za-z][^\s,:]*\s+){1,8}\d+[ab]?(?![\d:])")


def _shape_rx(expected_citation: str) -> "re.Pattern[str]":
    if re.search(r"\d\s*:\s*\d", expected_citation):
        return _COLON_CITE
    if re.search(r"[Pp]ara", expected_citation):
        return _PARA_CITE
    return _NUM_CITE


def _citation_candidates(answer: str, expected_citation: str) -> set[str]:
    rx = _shape_rx(expected_citation)
    return {normalize(m.group(0)) for m in rx.finditer(answer)}


def bounded_contains(answer: str, expected: str) -> bool:
    """LEGACY FLOOR / boundary-aware equality primitive — **not** the text-retrieval scoring
    contract. The full normalized ``expected`` appears in ``answer`` with word boundaries (so
    ``Jude 1:3`` does not match ``Jude 1:30``), not mere substring containment.

    Since Spec 52 the public text-retrieval containment contract is :func:`fold_aware_contains`
    (a strict SUPERSET of this that also credits Uthmani↔Imla'i orthographic matches); this
    predicate is its superset FLOOR. Call it directly ONLY where boundary-aware *equality* is the
    intended semantics and the orthography fold must NOT apply — today that is ``cite_passage``
    citation matching (`_single_citation_correct`) and the ``normalize``-only edition identity
    checks. **New text-retrieval analyses must use** :func:`fold_aware_contains`, not this, or they
    will silently score the obsolete pre-#52 (orthography-blind) semantics. (PR #62 review,
    architect round-1 item 4.)"""
    ne = normalize(expected)
    return re.search(r"(?<!\w)" + re.escape(ne) + r"(?!\w)", normalize(answer)) is not None



def _single_citation_correct(answer: str, expected_citation: str) -> tuple[int, int]:
    """Returns (correct, n_candidates). A multi-candidate answer scores 0; otherwise
    the single candidate must EQUAL ground truth (boundary-aware, not containment).

    Spans that all assert the EXPECTED citation count as ONE candidate however many
    times the model repeats it ("It is Jude 1:3. Jude 1:3 warns…") — repetition is
    not a hedge; only distinct OTHER citations are."""
    cands = _citation_candidates(answer, expected_citation)
    ne = normalize(expected_citation)
    boundary = re.compile(r"(?<!\w)" + re.escape(ne) + r"(?!\w)")
    matching = {c for c in cands if boundary.search(c)}
    others = cands - matching
    n = (1 if matching else 0) + len(others)
    if n > 1:
        return 0, n  # offered more than one DISTINCT citation candidate -> hedge
    # cite_passage stays on bounded_contains, NOT the Spec 52 orthography fold (PR review, architect
    # round-1 item 3): the task contract is boundary-aware citation EQUALITY, not verse-length
    # containment, and the fold's whitespace-flex + optional-alef is looser than a citation match
    # wants on SHORT strings — exactly where the collision residue bites hardest. A no-op on all
    # committed evidence (citations are Latin/numeric, 0 Arabic), so nothing moves. When #39
    # introduces Arabic-script citations, design a citation-appropriate equivalence then (its own
    # collision analysis) rather than silently inheriting the verse-length fold.
    return int(bounded_contains(answer, expected_citation)), n


def score_answer(task: str, answer: str, expected: dict, graders: "list | None" = None) -> dict:
    """Score one model answer. Returns the metrics dict described in the module docstring.

    For the text-retrieval tasks the reported submetric fields and the headline are determined by
    the selected ``graders`` (a list of ``graders.Grader``; ``None`` ⇒ the default deterministic
    set): each grader contributes its ``metric_keys`` and the headline ``correct`` is the OR of the
    selected graders' verdicts. ``token_f1`` is an always-on diagnostic. The default set
    ``{strict, containment}`` emits ``exact``/``normalized``/``token_f1``/``contains_reference`` with
    ``correct = normalized OR contains_reference`` — identical to the frozen phase-1 contract."""
    if task in ("retrieve_quote", "complete_unit"):
        from .graders import GraderError, resolve_evaluators, submetrics_for

        if graders is None:
            graders = resolve_evaluators(None)
        elif not graders:
            raise GraderError("empty grader list passed to score_answer")
        target = expected["text"]
        # all primitives are computed; only the selected graders' fields (+ always-on token_f1)
        # are emitted. contains_reference uses fold_aware_contains (Spec 52) — a strict SUPERSET
        # of bounded_contains that also credits an Uthmani↔Imla'i orthographic match; the
        # bool(normalize(target)) guard stops an empty reference (whose escaped regex matches
        # everywhere) from scoring 1. Containment is confined to these two text-retrieval tasks —
        # the provenance branches below never see it.
        computed = {
            "exact": int(answer.strip() == target.strip()),
            "normalized": int(normalize(answer) == normalize(target)),
            "token_f1": round(token_f1(answer, target), 4),
            "token_f1_base": round(token_f1_base(answer, target), 4),
            "contains_reference": int(bool(normalize(target)) and fold_aware_contains(answer, target)),
        }
        metrics = {k: computed[k] for k in submetrics_for(graders)}  # canonical order
        metrics["correct"] = int(any(g.verdict(computed) for g in graders))
        return _with_outcome(metrics, task, answer, expected)
    if task == "verify_source":
        parsed = parse_yes_no(answer)
        correct = int(parsed == expected["answer"])
        return _with_outcome(
            {"parsed": parsed, "expected": expected["answer"], "correct": correct},
            task, answer, expected,
        )
    if task == "cite_passage":
        correct, n = _single_citation_correct(answer, expected["citation"])
        return _with_outcome({"correct": correct, "n_candidates": n}, task, answer, expected)
    raise ScoreError(f"unknown task {task!r}")


def _with_outcome(metrics: dict, task: str, answer: str, expected: dict) -> dict:
    """Stamp ``outcome`` ∈ {correct, incorrect, refused} onto a metrics dict (Spec 15, decision #2).

    Refusal is an OUTCOME, not a grader: a declined cell short-circuits the headline (``correct`` is
    forced to 0) and is reported as ``refused`` so it is excluded from accuracy. All submetrics the
    grader(s) already computed are kept unchanged — a refused text-retrieval cell still carries its
    exact/normalized/token_f1/contains_reference (preserving the phase-1 projection oracle). For a
    non-refused cell the outcome is simply correct-vs-incorrect per the headline verdict."""
    from .outcomes import classify_refusal

    if task == "verify_source":
        # verify_source's "answer" IS the verdict, so refusal is determined by whether a verdict was
        # COMMITTED, not by a decline-cue scan: a committed leading Yes/No (``parsed`` is not None) is
        # GRADED even when followed by a disclaimer ("No, though I cannot fully verify…"); the absence
        # of a leading verdict (``parsed`` is None — a decline, a non-committal answer, or a
        # negation-evasion like "there is no way to verify this … yes") is a refusal to answer the
        # yes/no question. This both closes the #23 gaming gap and does not force a declined-but-
        # committed verdict to ``refused``.
        refused = metrics.get("parsed") is None
    else:
        # A decline-prefixed answer that still DELIVERS the right result (a hedged-but-correct
        # citation, "I can't verify, but it's Jude 1:3") is an ANSWER, not a refusal — so for the
        # tasks whose correctness is a DELIVERED result, refusal only applies when the headline is
        # not already correct.
        refused = classify_refusal(answer, task, expected) and not metrics["correct"]
    if refused:
        metrics["correct"] = 0  # headline skipped for a refused cell (no-op when already 0)
        metrics["outcome"] = "refused"
    else:
        metrics["outcome"] = "correct" if metrics["correct"] else "incorrect"
    return metrics


def _outcome_cell(acc: dict, submetric_keys: tuple[str, ...]) -> dict:
    """Build a summary cell with the three-outcome split + coverage (Spec 15, decision #2).

    - ``accuracy = correct/(correct+incorrect)`` — refusals EXCLUDED (``None`` when nothing was
      graded, i.e. every answered cell was refused); "how often it's right *when it answers*".
    - ``coverage = (correct+incorrect)/n`` — "how often it answers" (the honest companion that
      stops an all-but-one-refused model's 100% from being read as a clean sweep).
    - ``refused_rate = refused/n``; ``correct``/``incorrect``/``refused`` are the raw counts.

    Submetric averages are taken over the GRADED cells (correct+incorrect), never ``n`` — a refusal
    is not graded, so it must not dilute the diagnostic averages. ``missing`` (roster cells that
    produced no answer) is added by the caller and stays distinct from ``refused`` (answered, declined).
    """
    n = acc["n"]
    refused = acc.get("refused", 0)
    correct = acc["correct"]
    graded = n - refused
    cell = {
        "n": n,
        "accuracy": round(correct / graded, 4) if graded else None,
        "coverage": round(graded / n, 4) if n else None,
        "correct": correct,
        "incorrect": graded - correct,
        "refused": refused,
        "refused_rate": round(refused / n, 4) if n else None,
    }
    for sm in submetric_keys:
        cell[sm] = round(acc[sm] / graded, 4) if graded else None
    return cell


def score_file(
    answers_path: Path, scores_path: Path, expected: dict[tuple[str, str], int] | None = None,
    expected_tradition: dict[tuple[str, str, str], int] | None = None,
    panel: dict[str, dict] | None = None,
    expected_digest: str | None = None,
    evaluators: "list[str] | None" = None,
    expected_text: dict[tuple[str, str, str], int] | None = None,
    judgments: Path | None = None,
) -> dict:
    """Score every answer row; write per-answer scores and return the summary dict.

    Scoring sees only successful answer rows (``collect`` leaves failed cells
    pending and exits non-zero). Pass ``expected`` — a ``{(model_id, task): count}``
    roster (the panel × question set) — to **represent missing/failed cells**: each
    cell then reports ``expected_n`` and ``missing``, and a model whose cells ALL
    failed still appears (``n=0``, everything missing) instead of vanishing. Without
    it, the summary reflects only what is present (a model missing some tasks renders
    ``—`` for them)."""
    if not answers_path.exists():
        raise ScoreError(f"{answers_path}: no answers file")
    rows = []
    with open(answers_path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            if not line.strip():
                continue
            d = json.loads(line)
            for key in ("question_id", "model_id", "task", "answer", "question"):
                if key not in d:
                    raise ScoreError(f"{answers_path}:{line_no}: answer row missing '{key}'")
            rows.append(d)
    if not rows:
        raise ScoreError(f"{answers_path}: no answer rows")

    # all answers must come from one question set (collect stamps the digest on
    # every row); a missing digest means a foreign/pre-digest file
    digests = {d.get("question_set_digest") for d in rows}
    if None in digests or "" in digests:
        raise ScoreError(
            f"{answers_path}: answer row(s) carry no question_set_digest — refusing a "
            "foreign/legacy answers file"
        )
    if len(digests) > 1:
        raise ScoreError(
            f"{answers_path}: mixes {len(digests)} question sets {sorted(digests)} — "
            "answers from different generate runs must not be scored together"
        )
    # bind to the question set the roster was built from: scoring run A's answers
    # against run B's questions would silently produce a wrong roster / panel
    if expected_digest is not None:
        answers_digest = next(iter(digests))
        if answers_digest != expected_digest:
            raise ScoreError(
                f"{answers_path}: answers' question_set_digest {answers_digest} does not match "
                f"the --questions digest {expected_digest} — scoring answers against a different "
                "question set than they were collected for; point --questions at the matching set"
            )

    # Explicit judge-provenance opt-in (Spec 21): with --judgments, bind the sidecar's manifest to
    # these answers' question set and stamp the resolved judge build into the summary. Validated HERE,
    # before any scores.jsonl is written, so a mismatch fails fast without a half-written side effect.
    # Without --judgments, default `score` never reads a sidecar and the summary is unchanged.
    judge_provenance: dict | None = None
    if judgments is not None:
        from . import jev

        # bind the sidecar to THESE answers: (question_id, model_id, answer_digest) per answer row, so
        # a sidecar from a different collection (same question set) cannot stamp false provenance
        answer_keys = {
            (r["question_id"], r["model_id"], jev.answer_digest(r.get("answer") or ""))
            for r in rows
        }
        judge_provenance = jev.load_provenance(
            judgments, question_set_digest=next(iter(digests)), answer_keys=answer_keys
        )

    # resolve the grader selection ONCE (default = deterministic set); it drives both the emitted
    # text-retrieval submetric fields and which submetrics the summary aggregates.
    from .graders import resolve_evaluators, submetrics_for

    graders = resolve_evaluators(evaluators)
    text_submetrics = submetrics_for(graders)  # canonical-ordered keys for retrieve_quote/complete_unit

    def _task_submetrics(task: str) -> tuple[str, ...]:
        if task in ("retrieve_quote", "complete_unit"):
            return text_submetrics
        return _SUBMETRICS.get(task, ())  # () for verify_source / cite_passage (no fixed submetrics)

    scores_path.parent.mkdir(parents=True, exist_ok=True)
    per_cell: dict[tuple[str, str], dict] = {}  # (model_id, task) -> accumulators
    per_trad: dict[tuple[str, str, str], dict] = {}  # (model_id, tradition, task) -> {n, correct}
    per_text: dict[tuple[str, str, str], dict] = {}  # (model_id, text_label, task) -> {n, correct, refused}
    usage: dict[str, dict] = {}  # model_id -> {calls, in, out, model, served_by{host:count}}
    with open(scores_path, "w", encoding="utf-8") as out:
        for d in rows:
            metrics = score_answer(d["task"], d["answer"], d["question"]["expected"], graders)
            out.write(
                json.dumps(
                    {
                        "question_id": d["question_id"],
                        "model_id": d["model_id"],
                        "task": d["task"],
                        "metrics": metrics,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
            # accumulator seeded from THIS task's selected submetrics (canonical order), so a
            # subset selection never leaves a stale key (e.g. `--evaluator strict` must not emit a
            # spurious contains_reference:0.0 into the summary) and the summary loop reads acc[sm].
            sm_keys = _task_submetrics(d["task"])
            acc = per_cell.setdefault(
                (d["model_id"], d["task"]),
                {"n": 0, "correct": 0, "refused": 0, **{k: 0 for k in sm_keys}},
            )
            refused = metrics.get("outcome") == "refused"
            acc["n"] += 1
            acc["correct"] += metrics["correct"]
            acc["refused"] += int(refused)
            # submetrics accumulate over GRADED cells only (refusals are never graded, so they must
            # not dilute the diagnostic averages); the per-cell values are still emitted on refused rows.
            if not refused:
                for sm in sm_keys:
                    acc[sm] += metrics[sm]  # sm_keys derives from the same selection ⇒ present (fail loud if not)
            # token usage for cost accounting (recorded per answer row by collect)
            u = d.get("usage") or {}
            um = usage.setdefault(
                d["model_id"], {"calls": 0, "in": 0, "out": 0, "model": d.get("model"), "served_by": {}}
            )
            um["calls"] += 1
            um["in"] += int(u.get("in", 0) or 0)
            um["out"] += int(u.get("out", 0) or 0)
            host = u.get("provider")  # OpenRouter reports the upstream serving host
            if host:
                um["served_by"][host] = um["served_by"].get(host, 0) + 1
            src = d.get("question", {}).get("source", {})
            # tradition breakdown: count this observation once PER listed tradition
            for trad in src.get("tradition", []) or []:
                tacc = per_trad.setdefault(
                    (d["model_id"], trad, d["task"]), {"n": 0, "correct": 0, "refused": 0}
                )
                tacc["n"] += 1
                tacc["correct"] += metrics["correct"]
                tacc["refused"] += int(refused)
            # per-text breakdown (one text = one (work, version, language)); a verify_source
            # negative aggregates under the ASKED edition (Phase-2 source), the right denominator
            # now that per-tradition balance no longer holds (9 of 17 texts are hadith collections).
            tkey = text_key(src)
            if tkey is not None:
                xacc = per_text.setdefault(
                    (d["model_id"], TEXT_KEY_SEP.join(tkey), d["task"]), {"n": 0, "correct": 0, "refused": 0}
                )
                xacc["n"] += 1
                xacc["correct"] += metrics["correct"]
                xacc["refused"] += int(refused)

    expected = expected or {}
    summary: dict = {"models": {}, "by_tradition": {}, "by_text": {}}
    # every (model, task) that was answered OR was expected (so a fully-failed
    # model/task is represented, not dropped)
    all_cells = set(per_cell) | set(expected)
    for (model_id, task) in sorted(all_cells):
        acc = per_cell.get((model_id, task))
        # a fully-missing (expected-but-unanswered) cell gets the same three-outcome schema via a
        # zero accumulator (accuracy/coverage/refused_rate → None, counts → 0), so summary consumers
        # see one shape; `missing` below stays distinct from `refused` (answered-then-declined).
        cell = _outcome_cell(acc or {"n": 0, "correct": 0, "refused": 0}, _task_submetrics(task))
        if (model_id, task) in expected:
            cell["expected_n"] = expected[(model_id, task)]
            cell["missing"] = max(expected[(model_id, task)] - cell["n"], 0)
        summary["models"].setdefault(model_id, {})[task] = cell
    # _overall from RAW counts (not a lossy round(accuracy*n) reconstruction)
    for model_id in summary["models"]:
        cells = [acc for (m, _), acc in per_cell.items() if m == model_id]
        ov = _outcome_cell(
            {
                "n": sum(c["n"] for c in cells),
                "correct": sum(c["correct"] for c in cells),
                "refused": sum(c["refused"] for c in cells),
            },
            (),
        )
        exp_total = sum(v for (m, _), v in expected.items() if m == model_id)
        if exp_total:
            ov["expected_n"] = exp_total
            ov["missing"] = max(exp_total - ov["n"], 0)
        summary["models"][model_id]["_overall"] = ov
    # per-model x tradition x task (each observation counted once per listed
    # tradition, so a tradition's n can exceed the overall count); overall-once
    # lives in summary["models"]. A tradition-aware roster surfaces missing/failed
    # cells here too (a fully-failed model x tradition x task is not dropped).
    expected_tradition = expected_tradition or {}
    all_trad_cells = set(per_trad) | set(expected_tradition)
    for (model_id, trad, task) in sorted(all_trad_cells):
        tacc = per_trad.get((model_id, trad, task))
        # tradition cells report outcomes, not submetrics; a fully-missing one uses the same schema
        cell = _outcome_cell(tacc or {"n": 0, "correct": 0, "refused": 0}, ())
        if (model_id, trad, task) in expected_tradition:
            cell["expected_n"] = expected_tradition[(model_id, trad, task)]
            cell["missing"] = max(expected_tradition[(model_id, trad, task)] - cell["n"], 0)
        summary["by_tradition"].setdefault(model_id, {}).setdefault(trad, {})[task] = cell
    for model_id, trads in summary["by_tradition"].items():
        for trad, tasks in trads.items():
            raw = [per_trad.get((model_id, trad, t), {"n": 0, "correct": 0, "refused": 0}) for t in tasks]
            ov = _outcome_cell(
                {
                    "n": sum(c["n"] for c in raw),
                    "correct": sum(c["correct"] for c in raw),
                    "refused": sum(c["refused"] for c in raw),
                },
                (),
            )
            exp_total = sum(v for (m, tr, _), v in expected_tradition.items() if m == model_id and tr == trad)
            if exp_total:
                ov["expected_n"] = exp_total
                ov["missing"] = max(exp_total - ov["n"], 0)
            tasks["_overall"] = ov

    # per-model x text x task: one text = one (work, version, language), the right denominator
    # now that per-tradition balance no longer holds (Spec 26). Carries outcomes
    # (accuracy/coverage/refused), never submetrics. Given the same roster treatment as the
    # model/task and tradition tables: a fully-missing (expected-but-unanswered) cell is
    # represented with expected_n/missing, so a text with a dropped cell shows `missing`, not a
    # silently short n (e.g. the gpt-oss empty cite_passage cell → n=27, missing=1).
    expected_text = expected_text or {}
    all_text_cells = set(per_text) | set(expected_text)
    for (model_id, text_label, task) in sorted(all_text_cells):
        cell = _outcome_cell(per_text.get((model_id, text_label, task)) or {"n": 0, "correct": 0, "refused": 0}, ())
        if (model_id, text_label, task) in expected_text:
            cell["expected_n"] = expected_text[(model_id, text_label, task)]
            cell["missing"] = max(expected_text[(model_id, text_label, task)] - cell["n"], 0)
        summary["by_text"].setdefault(model_id, {}).setdefault(text_label, {})[task] = cell
    for model_id, texts in summary["by_text"].items():
        for text_label, tasks in texts.items():
            raw = [per_text.get((model_id, text_label, t), {"n": 0, "correct": 0, "refused": 0}) for t in tasks]
            ov = _outcome_cell(
                {
                    "n": sum(c["n"] for c in raw),
                    "correct": sum(c["correct"] for c in raw),
                    "refused": sum(c["refused"] for c in raw),
                },
                (),
            )
            exp_total = sum(v for (m, tl, _), v in expected_text.items() if m == model_id and tl == text_label)
            if exp_total:
                ov["expected_n"] = exp_total
                ov["missing"] = max(exp_total - ov["n"], 0)
            tasks["_overall"] = ov

    # Token usage totals (cost accounting). Prices are NOT invented: a cost appears
    # only for models whose panel entry supplied price_in/price_out ($ per 1M tokens).
    panel = panel or {}
    per_model_usage: dict[str, dict] = {}
    total = {"calls": 0, "in": 0, "out": 0}
    cost_total = 0.0
    n_priced = 0
    model_ids = sorted(set(usage) | set(panel))
    for model_id in model_ids:
        um = usage.get(model_id, {"calls": 0, "in": 0, "out": 0})
        row = {"calls": um["calls"], "in": um["in"], "out": um["out"]}
        p = panel.get(model_id, {})
        if p.get("price_in") is not None and p.get("price_out") is not None:
            row["cost_usd"] = round(um["in"] / 1e6 * p["price_in"] + um["out"] / 1e6 * p["price_out"], 6)
            cost_total += row["cost_usd"]
            n_priced += 1
        per_model_usage[model_id] = row
        for k in total:
            total[k] += um.get(k, 0)
    # a TOTAL cost is reported only when EVERY model is priced — a subtotal over a
    # subset of the panel would misrepresent itself as the run's cost
    if model_ids and n_priced == len(model_ids):
        total["cost_usd"] = round(cost_total, 6)
    summary["usage"] = {"per_model": per_model_usage, "total": total}

    # Panel composition, so the ≥3-model / ≥2-provider bar is checkable from the
    # committed artifact itself (no secrets — provider, model, tools and endpoint host only).
    # Only emitted when a run config was supplied: without it there is no provider/
    # endpoint to prove, and a table of blanks under a "proof" heading would mislead.
    if panel:
        summary["panel"] = {}
        for model_id in sorted(set(usage) | set(panel)):
            um = usage.get(model_id, {})
            p = panel.get(model_id, {})
            summary["panel"][model_id] = {
                "provider": p.get("provider"),
                "model": p.get("model") or um.get("model"),
                # tools is part of panel identity (Approach B): the viewer keys standings
                # on (provider, model, tools). A synthesised entry (usage with no panel)
                # defaults to [] so a bare model keys identically to a no-tools config.
                "tools": p.get("tools") or [],
                "endpoint": p.get("endpoint"),
                "max_tokens": p.get("max_tokens"),
                "temperature": p.get("temperature"),
                "served_by": sorted(um.get("served_by", {})) or None,
            }
    # Evaluator provenance (Spec 15, decision #5): which named graders decided the headline for the
    # text-retrieval cells in THIS summary, in selection order. The default set is {strict, containment};
    # a `--evaluator` subset is recorded here so a summary is self-describing about its scoring contract.
    summary["evaluators"] = [g.name for g in graders]
    # Judge provenance (Spec 21): a SIBLING key to `evaluators`, present only with --judgments, so the
    # summary states which resolved judge build produced any sidecar verdicts. `evaluators` stays a
    # list[str] (LeaderboardTable.tsx:48 / test_score.py) and no cost/usage field enters the summary
    # (test_tutorial_run.py). The judge never joins the deterministic headline.
    if judge_provenance is not None:
        summary["judge"] = judge_provenance
    # Additive run timestamp (Issue #7 pipeline half): a committed, mtime-independent
    # recency signal. The current viewer ignores it; it never affects scoring.
    summary["generated_at"] = datetime.now(timezone.utc).isoformat()
    return summary


def _cell_str(c: dict | None) -> str:
    """Render one table cell: '—' if absent, 'miss N' if expected-but-unanswered, otherwise
    'acc% cov cov% (n=N; c/i/r C/I/R)' — accuracy is right-when-it-answers (n/a if all refused),
    coverage sits beside it, and the correct/incorrect/refused counts are shown so the three-outcome
    split (and refused_rate = R/N) is readable from summary.md itself. '−missing' flags unanswered
    roster cells (distinct from refused)."""
    if c is None:
        return "—"
    if c["n"] == 0:
        return f"miss {c['missing']}" if c.get("missing") else "—"
    acc = "n/a" if c.get("accuracy") is None else f"{c['accuracy']:.0%}"
    s = acc
    if c.get("coverage") is not None:
        s += f" cov {c['coverage']:.0%}"
    if "correct" in c:  # scored cell: spec requires correct/incorrect/refused in summary.md
        s += f" (n={c['n']}; c/i/r {c['correct']}/{c['incorrect']}/{c['refused']})"
    else:
        s += f" (n={c['n']})"
    if c.get("missing"):
        s += f" −{c['missing']}"
    return s


def summary_markdown(summary: dict) -> str:
    """Render the summary: a models × tasks table, then a per-tradition breakdown.
    Missing model×task cells are shown ('—' / 'miss N'), never dropped."""
    models = summary["models"]
    tasks = sorted({t for m in models.values() for t in m if t != "_overall"})
    lines = ["| model | " + " | ".join(tasks) + " | overall |", "|" + "---|" * (len(tasks) + 2)]
    ranked = sorted(
        models.items(),
        key=lambda kv: -kv[1]["_overall"]["accuracy"] if kv[1]["_overall"]["accuracy"] is not None else 1,
    )
    for model_id, cells in ranked:
        row = [model_id] + [_cell_str(cells.get(t)) for t in tasks]
        ov = cells["_overall"]
        overall = "**n/a**" if ov["accuracy"] is None else f"**{ov['accuracy']:.0%}**"
        if ov.get("coverage") is not None:
            overall += f" cov {ov['coverage']:.0%}"
        if "correct" in ov:
            overall += f" (c/i/r {ov['correct']}/{ov['incorrect']}/{ov['refused']})"
        if ov.get("missing"):
            overall += f" −{ov['missing']}"
        row.append(overall)
        lines.append("| " + " | ".join(row) + " |")
    lines += [
        "",
        "_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). "
        "accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; "
        "refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._",
    ]

    by_trad = summary.get("by_tradition") or {}
    if by_trad:
        lines += ["", "### By tradition (each observation counts once per listed tradition)"]
        lines += ["| model | tradition | " + " | ".join(tasks) + " | overall |", "|" + "---|" * (len(tasks) + 3)]
        for model_id in sorted(by_trad):
            for trad in sorted(by_trad[model_id]):
                cells = by_trad[model_id][trad]
                row = [model_id, trad] + [_cell_str(cells.get(t)) for t in tasks]
                ov = cells["_overall"]
                acc = "n/a" if ov["accuracy"] is None else f"{ov['accuracy']:.0%}"
                cov = "" if ov.get("coverage") is None else f" cov {ov['coverage']:.0%}"
                cir = f"; c/i/r {ov['correct']}/{ov['incorrect']}/{ov['refused']}" if "correct" in ov else ""
                row.append(f"**{acc}**{cov} (n={ov['n']}{cir})")
                lines.append("| " + " | ".join(row) + " |")

    by_text = summary.get("by_text") or {}
    if by_text:
        # per-text table (Spec 26): each text's OVERALL — text, n, accuracy, coverage, refused — the
        # right denominator now that per-tradition balance no longer holds. One section per model.
        lines += ["", "### By text (one text = one work · version · language)"]
        for model_id in sorted(by_text):
            lines += ["", f"**{model_id}**",
                      "| text | n | accuracy | coverage | refused | missing |", "|" + "---|" * 6]
            for key in sorted(by_text[model_id]):
                ov = by_text[model_id][key]["_overall"]
                acc = "n/a" if ov["accuracy"] is None else f"{ov['accuracy']:.0%}"
                cov = "n/a" if ov.get("coverage") is None else f"{ov['coverage']:.0%}"
                miss = ov.get("missing") or 0
                lines.append(
                    f"| {_text_label_display(key)} | {ov['n']} | {acc} | {cov} | {ov['refused']} "
                    f"| {miss if miss else '—'} |"
                )

    panel = summary.get("panel") or {}
    if panel:
        lines += ["", "### Panel composition (committed-artifact proof — provider / model / tools / endpoint, no secrets)"]
        lines += [
            "| model_id | provider | model | tools | endpoint | max_tokens | temperature | served_by |",
            "|" + "---|" * 8,
        ]
        for mid in sorted(panel):
            p = panel[mid]
            served = ", ".join(p.get("served_by") or []) or "—"
            tools = ", ".join(p.get("tools") or []) or "—"
            max_tokens = "—" if p.get("max_tokens") is None else p.get("max_tokens")
            temperature = "—" if p.get("temperature") is None else p.get("temperature")
            lines.append(
                f"| {mid} | {p.get('provider') or '—'} | {p.get('model') or '—'} "
                f"| {tools} | {p.get('endpoint') or '—'} | {max_tokens} | {temperature} | {served} |"
            )

    usage = summary.get("usage") or {}
    if usage.get("per_model"):
        per = usage["per_model"]
        t = usage["total"]
        # show the cost column whenever ANY model is priced; unpriced models and (under
        # partial pricing) the total render "n/a" rather than a misleading $0.0000
        has_cost = any("cost_usd" in u for u in per.values())
        lines += ["", "### Token usage", "| model_id | calls | in | out |" + (" cost (USD) |" if has_cost else "")]
        lines += ["|" + "---|" * (5 if has_cost else 4)]
        for mid in sorted(per):
            u = per[mid]
            row = f"| {mid} | {u['calls']} | {u['in']:,} | {u['out']:,} |"
            if has_cost:
                row += f" ${u['cost_usd']:.4f} |" if "cost_usd" in u else " n/a |"
            lines.append(row)
        trow = f"| **total** | {t['calls']} | {t['in']:,} | {t['out']:,} |"
        if has_cost:
            trow += f" ${t['cost_usd']:.4f} |" if "cost_usd" in t else " n/a (partial pricing) |"
        lines.append(trow)
    return "\n".join(lines) + "\n"
