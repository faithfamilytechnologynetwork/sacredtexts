"""Talmud containment fold (issue #149): the owner's Talmud normalization guide, for the Aramaic
Talmud Bavli only.

Sefaria's Aramaic Talmud spells out what printings and models abbreviate (``אף על פי`` for
``אע״פ``), keeps a word where a model writes the censors' substitute (``נכרי`` for ``גוי``), and
differs in small regular spellings (``הימנו``/``ממנו``, ``וחייבים``/``וחייבין``, a leading ``ו``). A
model that quotes the passage in the other spelling has the right words.

``talmud_contains`` reads both sides into a word lattice. Each token is one unit holding its
readings, and the reference is contained when one of its paths appears in the answer. An ambiguous
form keeps every reading and its own spelling, so ``א״ר`` or ``ה׳`` takes whichever reading the other
side has. Abbreviations are only ever expanded; a full name is never collapsed to a form, so
``רבי יהודה`` and ``רבי יוסי`` stay distinct although both are ``ר״י``. Abbreviations are read before
numerals (``בר״ה`` is ב + ראש השנה, not 207).

The guide is data (``talmud_normalization_terms.tsv``, loaded once). A row of a data category
becomes a table entry. A rule row (orthography, prefix, punctuation, the numeral ranges) switches on
the rule written for it here. An unknown row fails the load. ``review only`` and ``DO NOT
normalize`` rows stay in the file and are skipped. Niqqud and cantillation are removed by
``strip_script_marks``, as in ``normalize()``.

Scoring only: ``score.fold_aware_contains`` calls this when the cell's work is the Talmud Bavli and
the reference is in Hebrew script. ``normalize()`` and the equality submetrics do not change.

Accepted collisions (credit-only; every other word of the passage must still line up). The guide's
``-ים``/``-ין`` rule covers words of 3+ letters, so ``מים`` (water) reads as ``מין`` and ``ימים`` (days)
as ``ימין`` (right hand). The guide spells
8 ``שמנה`` as well as ``שמונה``, so the tens rule reads ``שמנים`` (oils) as 80. The censorship rows
fold ``כותי`` and ``ארמאי`` everywhere, though their notes say "check per passage". These are the
owner's rules, kept as written; ``test_talmud_fold.py`` pins them so a change is deliberate.
"""
from __future__ import annotations

import csv
import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from .citations import hebrew_numeral
from .score import strip_script_marks

TALMUD_WORK = "Talmud Bavli"
TERMS_PATH = Path(__file__).with_name("talmud_normalization_terms.tsv")

GERESH, GERSHAYIM = "׳", "״"
_PREFIX_LETTERS = frozenset("והבכלמשד")  # one-letter prefixes that attach to a form (בר״ה, לגוי)
_NOT_APPLIED = frozenset({"review only", "DO NOT normalize"})
# The guide's rule rows (form column) -> the rule this module implements for each.
_RULE_ROWS = {
    "י״א … צ״ט": "gershayim_numeral",  # two letters with gershayim: the sum of the letter values
    "עשרים … תשעים / מאה / מאתים": "tens",  # tens words from the unit words, plus 100 and 200
    "-ים (word-final)": "final_im",
    "וו (doubled)": "double_vav",
    "יי (doubled)": "double_yod",
    "ו- (leading)": "leading_vav",
    "את ה-": "et_ha",
    "geresh / gershayim / quotation marks": "geresh",
    "niqqud and cantillation": "niqqud",
}
_TOKEN = re.compile(rf"[\w{GERESH}{GERSHAYIM}]+")
_MARKS = re.compile(f"[{GERESH}{GERSHAYIM}]+")
# Tens letter + units letter, and ט״ו / ט״ז, the usual spellings of 15 and 16.
_TWO_LETTER_NUMERAL = re.compile(f"[י-צ]{GERSHAYIM}[א-ט]|ט{GERSHAYIM}[וז]")
_ROUND_NUMBER = re.compile(r"([והבכלמשד]{0,2})([1-9]0*)")  # a prefix may lead: ב20 from בעשרים

Unit = frozenset  # of readings; a reading is a tuple of words


class TalmudGuideError(Exception):
    pass


@dataclass(frozen=True)
class Guide:
    readings: dict[str, Unit]  # a token -> its readings (abbreviation, class token, letter numeral)
    phrases: dict[tuple[str, ...], str]  # a folded multi-word form -> its class token
    words: dict[str, str]  # a folded whole word -> its canonical word (lexical, אלקים, number words)
    rules: frozenset[str]


def _fold_word(word: str, rules: frozenset[str]) -> str:
    if "double_vav" in rules:
        word = re.sub("ו{2,}", "ו", word)
    if "double_yod" in rules:
        word = re.sub("י{2,}", "י", word)
    if "leading_vav" in rules and len(word) >= 3 and word.startswith("ו"):
        word = word[1:]
    if "final_im" in rules and len(word) >= 3 and word.endswith("ים"):
        word = word[:-2] + "ין"
    return word


@lru_cache(maxsize=1)
def guide() -> Guide:
    with TERMS_PATH.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    abbreviations = {r["form"] for r in rows if r["category"] == "abbreviation"}
    readings: dict[str, set] = {}
    phrases: dict[tuple[str, ...], str] = {}
    words: dict[str, str] = {}
    numbers: dict[str, int] = {}
    rules: set[str] = set()
    for r in rows:
        form, to, category = r["form"], r["normalizes_to"], r["category"]
        if category in _NOT_APPLIED or (not category and form.startswith("---")):
            continue
        if form in _RULE_ROWS:
            rules.add(_RULE_ROWS[form])
        elif category == "abbreviation":
            readings.setdefault(form, set()).update(tuple(e.split()) for e in to.split(" | "))
        elif category in ("censorship", "divine name") and to.startswith("@"):
            if " " in form:  # עובד כוכבים; the row's note adds the plural עובדי and a trailing ומזלות
                head, *rest = form.split()
                for h in (head, head + "י"):
                    phrases[(h, *rest)] = phrases[(h, *rest, "ומזלות")] = to
            else:
                readings.setdefault(form, set()).add((to,))
        elif category in ("divine name", "lexical variant"):
            words[form] = to
        elif category == "numeral" and to.isdigit():
            for w in form.split(" / "):
                if not w.endswith(GERESH):
                    numbers[w] = int(to)
                elif w not in abbreviations:  # ר׳ is רבי / רב: the abbreviation reading wins
                    readings.setdefault(w, set()).add((to,))
        else:
            raise TalmudGuideError(f"{TERMS_PATH.name}: no rule for row {form!r} ({category!r})")
        if r["ambiguous"] == "yes" and form in readings:
            readings[form].add((form,))  # no reading matches the other side: the form stays as is
    if "tens" in rules:  # שלשה → שלשים (30), עשרה → עשרים (20); the ים→ין fold gives תלתין
        for w, v in list(numbers.items()):
            if 3 <= v <= 10:
                numbers[w.removesuffix("ה") + "ים"] = 20 if v == 10 else 10 * v
        numbers.update({"מאה": 100, "מאתים": 200})
    frozen = frozenset(rules)

    def fold(w: str) -> str:
        return _fold_word(w, frozen)

    return Guide(
        readings={k: Unit(v) for k, v in readings.items()},
        phrases={tuple(map(fold, k)): v for k, v in phrases.items()},
        words={fold(k): fold(v) for k, v in words.items()} | {fold(k): str(v) for k, v in numbers.items()},
        rules=frozen,
    )


def _readings(token: str, g: Guide) -> Unit | None:
    if token in g.readings:
        return g.readings[token]
    if "leading_vav" in g.rules and len(token) >= 3 and token[0] == "ו" and token[1:] in g.readings:
        return g.readings[token[1:]]
    for n in (1, 2):  # a prefix glued to the form: בר״ה, לה׳, והנכרי
        head, rest = token[:n], token[n:]
        if len(rest) >= 2 and set(head) <= _PREFIX_LETTERS and rest in g.readings:
            return Unit((head + alt[0], *alt[1:]) for alt in g.readings[rest])
    if "gershayim_numeral" in g.rules:  # after every table lookup, so בר״ה stays ב + ראש השנה
        for n in (0, 1, 2):  # a prefix may lead: בי״ג = ב13, as בשלשה עשר reads
            head, rest = token[:n], token[n:]
            if set(head) <= _PREFIX_LETTERS and _TWO_LETTER_NUMERAL.fullmatch(rest):
                return Unit({(head + str(hebrew_numeral(rest)),)})
    return None


def _word(unit: Unit) -> str | None:
    """The word of a unit with one single-word reading, else None."""
    if len(unit) == 1:
        (reading,) = unit
        if len(reading) == 1:
            return reading[0]
    return None


def _phrases(units: list[Unit], g: Guide) -> list[Unit]:
    out, i = [], 0
    while i < len(units):
        for n in (3, 2):
            ws = [_word(u) for u in units[i:i + n]]
            if len(ws) == n and None not in ws and (cls := _phrase(ws, g)):
                out.append(Unit({(cls,)}))
                i += n
                break
        else:
            out.append(units[i])
            i += 1
    return out


def _phrase(ws: list[str], g: Guide) -> str | None:
    for n in (0, 1, 2):
        head = ws[0][:n]
        if set(head) <= _PREFIX_LETTERS and (cls := g.phrases.get((ws[0][n:], *ws[1:]))):
            return head + cls
    return None


def _drop_et_ha(units: list[Unit]) -> list[Unit]:
    """``את היציע`` reads as ``יציע``: the object marker and the article are dropped."""
    out, i = [], 0
    while i < len(units):
        nxt = _word(units[i + 1]) if i + 1 < len(units) else None
        if _word(units[i]) == "את" and nxt and len(nxt) >= 3 and nxt.startswith("ה"):
            out.append(Unit({(nxt[1:],)}))
            i += 2
        else:
            out.append(units[i])
            i += 1
    return out


def _compounds(units: list[Unit]) -> list[Unit]:
    """Adjacent round numbers of different magnitude are summed: עשרים ואחד = 21, שלש עשרה = 13.
    A prefix stays on the first number: בעשרים ואחד = ב21, as בכ״א reads."""
    out: list[Unit] = []
    runs: list[tuple[str, int, set] | None] = []  # per unit of out: (prefix, sum, magnitudes) or None
    for u in units:
        w = _word(u)
        m = _ROUND_NUMBER.fullmatch(w) if w else None
        run = runs[-1] if runs else None
        if m and run and not m[1] and len(m[2]) not in run[2]:
            prefix, total, mags = run
            runs[-1] = (prefix, total + int(m[2]), mags | {len(m[2])})
            out[-1] = Unit({(f"{prefix}{total + int(m[2])}",)})
        else:
            out.append(u)
            runs.append((m[1], int(m[2]), {len(m[2])}) if m else None)
    return out


def talmud_units(text: str) -> list[Unit]:
    """``text`` as a list of units, each the set of its readings under the guide."""
    g = guide()
    s = unicodedata.normalize("NFKD", text)
    s = s.replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')
    s = strip_script_marks(s).casefold()
    if "geresh" in g.rules:
        s = s.replace("'", GERESH).replace('"', GERSHAYIM)
    units: list[Unit] = []
    for raw in _TOKEN.findall(s):
        token = raw.lstrip(GERESH + GERSHAYIM).rstrip(GERSHAYIM)  # quotation marks, not gershayim
        alts = _readings(token, g)
        if alts is not None:
            units.append(alts)
        else:
            units.extend(Unit({(w,)}) for w in _MARKS.split(token) if w)

    def canon(w: str) -> str:
        f = _fold_word(w, g.rules)
        if f in g.words:
            return g.words[f]
        for n in (1, 2):  # a prefix glued to the word: משלשה = מ + 3, as מג׳ reads
            head, rest = f[:n], f[n:]
            if len(rest) >= 2 and set(head) <= _PREFIX_LETTERS and rest in g.words:
                return head + g.words[rest]
        return f

    units = [Unit(tuple(map(canon, alt)) for alt in u) for u in units]
    units = _phrases(units, g)
    if "et_ha" in g.rules:
        units = _drop_et_ha(units)
    return _compounds(units)


def _lattice(units: list[Unit]) -> dict:
    """node -> [(word, next node)]. Unit boundaries are the ints 0..len(units); a multi-word
    reading threads its own nodes between two boundaries."""
    edges: dict = {}
    for i, unit in enumerate(units):
        for k, reading in enumerate(sorted(unit)):
            node = i
            for j, word in enumerate(reading):
                nxt = i + 1 if j == len(reading) - 1 else (i, k, j)
                edges.setdefault(node, []).append((word, nxt))
                node = nxt
    return edges


def talmud_contains(answer: str, expected: str) -> bool:
    """Some reading of the whole reference appears, word for word, in some reading of the answer.
    The match may start or end inside an expanded abbreviation, as a word-bounded match would."""
    ref_units = talmud_units(expected)
    if not ref_units:
        return False
    ans, ref, end = _lattice(talmud_units(answer)), _lattice(ref_units), len(ref_units)
    first = {w for w, _ in ref[0]}
    todo = [(node, 0) for node, out in ans.items() if any(w in first for w, _ in out)]
    seen = set(todo)
    while todo:
        a, r = todo.pop()
        for rw, r_next in ref[r]:
            for aw, a_next in ans.get(a, ()):
                if aw != rw:
                    continue
                if r_next == end:
                    return True
                if (a_next, r_next) not in seen:
                    seen.add((a_next, r_next))
                    todo.append((a_next, r_next))
    return False
