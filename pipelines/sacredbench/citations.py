"""Citation equivalence for ``cite_passage`` (issue #112).

A citation written in the text's own notation is the same citation as the expected one:
``Πράξεις 24:1`` is ``Acts 24:1``, ``שמות כח:מג`` is ``Exodus 28:43``, ``עירובין צ״א א׳:א׳`` is
``Eruvin 91a:1``, ``آل عمران: ١٧٤`` is ``3:174``. :func:`canonical_citation_text` rewrites an
answer into the expected citation's notation (Unicode digits to ASCII; native-script labels to the
English label, from ``citation_aliases.yaml``; Hebrew letter-numerals and amud letters to numbers
and ``a``/``b``; surah names to their number) so the boundary-aware single-citation matcher in
``score.py`` can compare it. Scoring-only: ``normalize()`` and every other task are untouched.

Granularity (owner decision, #112): a Talmud citation is conventionally tractate + daf + amud and a
Guru Granth Sahib citation is the Ang (page), but the expected citations also carry Sefaria's
segment / the line. With :data:`HEADLINE_DROPS_SEGMENT` on, those citations are scored at the
conventional unit and the full-granularity verdict is reported as ``segment_match``.

Since #135 a Guru Granth Sahib cite row asks for and expects the bare Ang (``Ang 315``), because line
numbering within an Ang is not standardised. A line the model volunteers (``Ang 315:9``) is dropped,
``Page 315`` is the Ang, and ``segment_match`` is None (no line to match).

:func:`score_citation` is credit-only: the headline is the existing matcher's verdict OR the
equivalence verdict, so a cell that scored correct before still does. The one exception is a
bare-Ang expected (#135): its headline is the Ang verdict alone, because the raw matcher would credit
a hedge there.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml

from .score import (
    _COLON_CITE,
    _citation_candidates,
    _shape_rx,
    _single_citation_correct,
    fold_citation_digits,
    normalize,
    strip_script_marks,
)

ALIASES_PATH = Path(__file__).with_name("citation_aliases.yaml")

# The #112 owner-decision switch. False scores Talmud and Guru Granth Sahib citations at the
# expected's full segment / line granularity again; segment_match is reported either way. A bare-Ang
# expected (#135) has no line, so the switch does not apply to it.
HEADLINE_DROPS_SEGMENT = True

_HEBREW_VALUES = dict(zip(
    "אבגדהוזחטיכךלמםנןסעפףצץקרשת",
    (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 20, 30, 40, 40, 50, 50, 60, 70, 80, 80, 90, 90, 100, 200, 300, 400),
))
_GERESH = "[\"'׳״]"  # ASCII or Hebrew geresh / gershayim
_HEB_NUM = rf"[א-ת](?:{_GERESH}?[א-ת]){{0,3}}{_GERESH}?"
# Word boundaries that also count Indic vowel signs (not \w) as part of the word.
_START = r"(?<![\wऀ-෿])"
_END = r"(?![\wऀ-෿])"

_DAF_CITATION = re.compile(r"\d+[ab]:\d+$")
_VERSE_CITATION = re.compile(r"\d+:\d+$")
_BARE_VERSE = re.compile(r"\d+:\d+")
_SEGMENTED = re.compile(r"(.+?) (\d+[ab]?):\d+")
_BARE_ANG = re.compile(r"Ang \d+")


def _fold(text: str) -> str:
    """The form both answers and alias tables are matched in: NFKD, Greek/Hebrew/Arabic marks
    removed, casefolded, Unicode decimal digits as ASCII, the Greek numeral sign (Β΄) dropped.
    Punctuation stays: a geresh or gershayim is part of a Hebrew numeral."""
    text = strip_script_marks(unicodedata.normalize("NFKD", text)).casefold()
    text = text.replace(" ́", "").replace("ʹ", "")  # Greek tonos / numeral sign after NFKD
    return fold_citation_digits(text)


def _alternation(keys) -> str:
    return "|".join(re.escape(k) for k in sorted(keys, key=len, reverse=True))


@dataclass(frozen=True)
class _Tables:
    native: dict[str, str]  # folded native form -> casefolded label
    chapters: dict[str, int]  # folded chapter name -> chapter number
    segmented: frozenset[str]  # casefolded labels whose citation ends in a segment index
    native_rx: re.Pattern
    verse_rx: re.Pattern
    daf_rx: re.Pattern
    chapter_rx: re.Pattern
    segment_rx: re.Pattern


def _register(table: dict, key: str, value, edition: str) -> None:
    if table.setdefault(key, value) != value:
        raise ValueError(f"{ALIASES_PATH.name}: {key!r} ({edition}) maps to both {table[key]!r} and {value!r}")


@lru_cache(maxsize=1)
def _tables() -> _Tables:
    data = yaml.safe_load(ALIASES_PATH.read_text(encoding="utf-8"))
    native: dict[str, str] = {}
    chapters: dict[str, int] = {}
    labels: set[str] = set()
    segmented: set[str] = set()
    for edition in data["editions"]:
        for label, forms in edition.get("labels", {}).items():
            canon = label.casefold()
            labels.add(canon)
            if edition.get("segment_indexed"):
                segmented.add(canon)
            for form in forms:
                _register(native, _fold(form), canon, edition["edition"])
        for number, names in edition.get("chapter_names", {}).items():
            for name in names:
                _register(chapters, _fold(name), int(number), edition["edition"])
    label = f"({_alternation(labels)})\\s+"
    return _Tables(
        native=native,
        chapters=chapters,
        segmented=frozenset(segmented),
        native_rx=re.compile(f"{_START}({_alternation(native)})['׳]?{_END}"),
        verse_rx=re.compile(f"{_START}{label}({_HEB_NUM})\\s*[:,]\\s*({_HEB_NUM})(?![א-ת])"),
        daf_rx=re.compile(
            f"{_START}{label}({_HEB_NUM})(?:\\s*,\\s*|\\s+)(?:ע{_GERESH}?)?([אב]){_GERESH}?"
            f"(?:\\s*[:,]\\s*({_HEB_NUM}|\\d+))?(?![א-ת])"
        ),
        chapter_rx=re.compile(
            f"{_START}(?:{_fold('سورة')}\\s+)?({_alternation(chapters)}){_END}\\s*[:،,]?\\s*"
            f"(?:{_fold('الآية')}|{_fold('آية')})?\\s*(\\d+)(?![\\d:])"
        ),
        segment_rx=re.compile(f"{_START}({_alternation(segmented)})\\s+(\\d+[ab]?)\\s*:\\s*\\d+"),
    )


def hebrew_numeral(token: str) -> int | None:
    """The value of a Hebrew letter-numeral (``כ״ח`` → 28, ``טו`` → 15, ``קעו`` → 176), or None
    when the letters are not in non-increasing order and so are not a numeral."""
    values = [_HEBREW_VALUES[ch] for ch in token if ch in _HEBREW_VALUES]
    if not values or any(b > a for a, b in zip(values, values[1:])):
        return None
    return sum(values)


def _verse(m: re.Match) -> str:
    chapter, verse = hebrew_numeral(m[2]), hebrew_numeral(m[3])
    return m[0] if chapter is None or verse is None else f"{m[1]} {chapter}:{verse}"


def _daf(m: re.Match) -> str:
    daf = hebrew_numeral(m[2])
    amud = "a" if m[3] == "א" else "b"
    if daf is None:
        return m[0]
    if m[4] is None:
        return f"{m[1]} {daf}{amud}"
    segment = int(m[4]) if m[4].isdigit() else hebrew_numeral(m[4])
    return m[0] if segment is None else f"{m[1]} {daf}{amud}:{segment}"


def canonical_citation_text(answer: str, expected_citation: str) -> str:
    """``answer`` rewritten into the notation of ``expected_citation`` (casefolded)."""
    t = _tables()
    text = t.native_rx.sub(lambda m: t.native[m[1]], _fold(answer))
    if _DAF_CITATION.search(expected_citation):
        text = t.daf_rx.sub(_daf, text)
    elif _VERSE_CITATION.search(expected_citation):
        text = t.verse_rx.sub(_verse, text)
    if _BARE_VERSE.fullmatch(expected_citation):
        text = t.chapter_rx.sub(lambda m: f"{t.chapters[m[1]]}:{m[2]}", text)
    return text


def _conventional_unit(expected_citation: str) -> str | None:
    """``Rosh Hashanah 21a`` for ``Rosh Hashanah 21a:2``, ``Ang 1297`` for ``Ang 1297:28``; None
    for a citation that carries no segment index."""
    m = _SEGMENTED.fullmatch(expected_citation)
    return f"{m[1]} {m[2]}" if m and m[1].casefold() in _tables().segmented else None


def _drop_segment(text: str, unit: str) -> str:
    """Drop the segment index from every citation of the unit's shape (daf+amud, or a bare page),
    so a Mishnah citation "Bekhorot 1:1" is not read as daf 1."""
    amud = unit[-1] in "ab"
    return _tables().segment_rx.sub(lambda m: f"{m[1]} {m[2]}" if (m[2][-1] in "ab") == amud else m[0], text)


# Over canonical_citation_text, where "ਅੰਗ ੩੧੫" is "ang 315". _TOKEN_END is _END that lets a danda (।/॥,
# inside the Indic range _END excludes) or the Gurmukhi abbreviation sign follow: "ਅੰਗ ੩੧੦।" is Ang 310,
# while "ang 3150" and "ang 1402ਵਾਂ" are still not Ang 315 / Ang 1402. The cite prompt asks for the
# "page (Ang)" (#135), so a page word followed by a number may be the Ang label.
_TOKEN_END = r"(?!(?![।॥੶])[\wऀ-෿])"
_ANG_RX = re.compile(f"{_START}ang\\s+(\\d+){_TOKEN_END}")
_PAGE_WORD = f"(?:page(?:\\s+no\\.?)?|pg\\.?|p\\.|{re.escape(_fold('ਪੰਨਾ'))})"
_PAGE_RX = re.compile(f"{_START}{_PAGE_WORD}(?=\\s*\\d)")
_PAGE_AFTER_ANG_RX = re.compile(f"({_START}ang\\s+\\d+(?:\\s*:\\s*\\d+)?)[\\s,;(\\[]*{_PAGE_WORD}\\s*\\d+{_TOKEN_END}")
_THOUSANDS_RX = re.compile(r"(?<=\d),(?=\d{3}(?!\d))")  # "Ang 1,402" is Ang 1402
_NEGATION = _alternation(_fold(w) for w in ("not", "ਨਹੀਂ"))
# A colon citation with no work name before it ("…, 1402:3", "(1402:3)"): no letter, Indic sign or
# digit directly before the number, nor a letter one space before.
_BARE_COLON_RX = re.compile(r"(?<![^\W\d_])(?<![ऀ-෿])(?<![^\W\d_]\s)(?<![ऀ-෿]\s)(?<!\d)(\d+)\s*:\s*\d+(?!\w)")


def _page_as_ang(text: str) -> str:
    """A page word (``page``, ``Page No.``, ``p.``, ``pg.``, ``ਪੰਨਾ``) directly after an Ang citation is a
    qualifier and is dropped (``Ang 315, page 2 of this shabad``, ``Ang 315 (page 2)``); anywhere else it
    is the Ang label, so ``Page 315`` is Ang 315 and ``Ang 315 or Page 316`` names two Angs."""
    return _PAGE_RX.sub("ang ", _PAGE_AFTER_ANG_RX.sub(r"\1", text))


def _ang_text(text: str, expected_citation: str) -> str:
    """``text`` in the expected's notation, thousands commas dropped, a page label read as Ang, each
    Ang's line dropped."""
    text = _THOUSANDS_RX.sub("", canonical_citation_text(text, expected_citation))
    return _drop_segment(_page_as_ang(text), expected_citation)


def _echo_rx(ang: int) -> re.Pattern:
    """A disclaimed echo of the form example: ``not Ang 306``, a bare ``(Ang 306)``, ``ਨਹੀਂ`` before or after."""
    a = f"ang\\s+{ang}{_TOKEN_END}"
    return re.compile(
        f"{_START}(?:{_NEGATION})\\s+{a}|\\(\\s*{a}\\s*\\)|{_START}{a}\\s+(?:{_NEGATION}){_TOKEN_END}"
    )


def _score_at_ang(answer: str, expected_citation: str, example: str | None) -> dict:
    """``cite_passage`` against a bare Ang (#135). A candidate is an Ang, or a colon citation of another
    work (``… or John 1:1``). A qualifier beside the Ang (``line 9``, ``Mehl 5``, ``ਮਹਲਾ ੫``, a raag) is
    not one, so an English answer and a Gurmukhi answer score alike. The form example's Ang is dropped
    only as a disclaimed echo (``Ang 315 (not Ang 306)``); offered beside the answer (``Ang 306 or Ang
    315``) it is a rival, because nearly every Sikh cite prompt shows the same example. The headline is
    this verdict alone: on the raw answer the no-colon extractor skips every ``Ang N:k`` span, so the
    containment fallback would credit a hedge. There is no line to match: ``segment_match`` is None.

    A bare ``N:k`` (no work name) restating a named Ang is that Ang's line, not a rival: ``Ang 1402
    (Raag Jaijavanti, 1402:3)`` is Ang 1402.

    Known limits, accepted on the #135 follow-up review: a page right after an Ang is a qualifier even
    with another number (``Ang 1402, Page 1403`` is Ang 1402), and the separator before it is read
    without its words (``Ang 1402, which is page 2 of this shabad`` and ``Ang 1402: page 2`` are hedges);
    a bare second number is not a candidate (``Ang 1402 or 1403``); an echo disclaimed away from the
    example (``(Note: Ang 306 is the example you gave.)``) is a rival; a labelled line of the same Ang is
    a rival (``Ang 1402 (SGGS 1402:3)``)."""
    target = int(expected_citation.split()[1])
    text = re.sub(r"\s+", " ", _ang_text(answer, expected_citation))
    named = {int(n) for n in _ANG_RX.findall(text)}
    if example is not None:
        for ang in {int(n) for n in _ANG_RX.findall(_ang_text(example, expected_citation))} - {target}:
            text = _echo_rx(ang).sub(" ", text)  # an example equal to the answer is never disclaimed away
    angs = {int(n) for n in _ANG_RX.findall(text)}
    text = _BARE_COLON_RX.sub(lambda m: " " if int(m[1]) in named else m[0], text)
    rivals = {normalize(m[0]) for m in _COLON_CITE.finditer(text)}
    n = int(target in angs) + len(angs - {target}) + len(rivals)
    return {"correct": int(target in angs and n == 1), "n_candidates": n, "segment_match": None}


def score_citation(answer: str, expected_citation: str, example: str | None = None) -> dict:
    """``cite_passage`` metrics: ``correct`` and ``n_candidates``, plus ``segment_match`` for a
    segment-indexed citation. ``correct`` is the existing matcher's verdict OR the equivalence
    verdict; ``n_candidates`` changes only on a cell the equivalence credits. ``example`` (the
    prompt's form example, #118) is not counted as a candidate beside another citation. A bare-Ang
    expected (#135) is scored by :func:`_score_at_ang` instead."""
    if _BARE_ANG.fullmatch(expected_citation):
        return _score_at_ang(answer, expected_citation, example)
    correct, n = _single_citation_correct(answer, expected_citation, example)
    metrics = {"correct": correct, "n_candidates": n}
    text = canonical_citation_text(answer, expected_citation)
    if example is not None:
        example = canonical_citation_text(example, expected_citation)
    unit = _conventional_unit(expected_citation)
    rivals: set[str] = set()
    if unit is not None:
        full, _ = _single_citation_correct(text, expected_citation, example)
        metrics["segment_match"] = int(correct or full)
        if HEADLINE_DROPS_SEGMENT:
            text = _drop_segment(text, unit)
            if example is not None:
                example = _drop_segment(example, unit)
            if _shape_rx(expected_citation) is not _shape_rx(unit):
                # "Ang 1297:28" loses its colon at the Ang, but the colon citations the full
                # citation's extractor counted ("… or John 1:1") are still rivals. The example
                # need not be consulted here: it is an entry of the same work by construction
                # (generate.py), so it is an "Ang N:M" and _drop_segment has already taken its colon.
                rivals = _citation_candidates(text, expected_citation)
            expected_citation = unit
    if not correct:
        credited, n = _single_citation_correct(text, expected_citation, example)
        if credited and not rivals:
            metrics.update(correct=1, n_candidates=n)
    return metrics
