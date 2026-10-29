"""Arabic orthography fold (Spec 52). The fold credits an Uthmani↔Imla'i orthographic match
WITHOUT touching `normalize()` or the equality submetrics: the symmetric letter folds (ى→ي, ء→ا)
live in `score_normalize`, and ALL the orthographic flexibility — including the OPTIONAL long-ā alef
that the defective-spelling class (هذا/ذلك/الرحمن) requires — lives in `fold_aware_contains`, which is
a strict SUPERSET of `bounded_contains`. So this can only ADD credit, never remove it.

These exercise the capability in isolation (Phase 1): `fold_aware_contains` is not yet wired into the
default scoring path, so `normalize()` and every committed score stay byte-identical (guarded by the
existing regression suites). Read-only; the corpus sweep reads the committed open-licensed QUL Qur'an.
"""
from __future__ import annotations

import json
import unicodedata
from collections import defaultdict
from pathlib import Path

from sacredbench.score import (
    _answer_plene_form,
    bounded_contains,
    fold_aware_contains,
    normalize,
    score_normalize,
    strip_script_marks,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
QUL = REPO_ROOT / "texts" / "raw" / "Sunni Islam" / "quran_uthmani_from_qul.json.json"


# --- symmetric letter folds: equal under score_normalize (both sides) ------------------------


def test_bare_maqsura_folds_to_ya():
    assert score_normalize("هدى") == score_normalize("هدي")


def test_standalone_hamza_folds_to_alef():
    # أَرَءَيْتُمْ (standalone ء) ↔ أَرَأَيْتُمْ (seated hamza); "drop" would be asymmetric
    assert score_normalize("أَرَءَيْتُمْ") == score_normalize("أَرَأَيْتُمْ")
    assert score_normalize("أَرَءَيْتُمْ") == "ارايتم"


def test_already_folded_cases_still_fold():
    assert score_normalize("آمن") == score_normalize("امن")          # alif madda (NFKD)
    assert score_normalize("ٱلله") == score_normalize("الله")         # wasl
    assert score_normalize("مؤمن") == score_normalize("مومن")         # hamza-on-waw (NFKD)


# --- the long-ā dagger is NOT folded in the equality path (defective spelling preserved) -----


def test_dagger_is_deleted_not_promoted_in_normalize_path():
    # Spec 52's core correction: the dagger must NOT become a letter in score_normalize, or the
    # DEFECTIVE-SPELLING class (Imla'i omits the alef) would be un-credited. It is deleted, as today.
    assert score_normalize("ذَٰلِكَ") == "ذلك"       # NOT ذالك
    assert score_normalize("هَٰذَا") == "هذا"         # NOT هاذا
    # and today's normalize() (unchanged) already matches these — no regression:
    assert normalize("ٱلرَّحْمَٰنِ") == normalize("الرحمن")
    assert normalize("ذَٰلِكَ") == normalize("ذلك")


# --- fold_aware_contains: the long-ā alef is OPTIONAL, so plene AND defective both match -------


def test_fold_contains_credits_long_aa_either_spelling():
    assert fold_aware_contains("الكتاب", "ٱلْكِتَٰبِ")      # plene: dagger ↔ written alef
    assert fold_aware_contains("سبحان", "سُبْحَٰنَ")          # plene
    assert fold_aware_contains("الرحمن", "ٱلرَّحْمَٰنِ")      # defective: Imla'i omits the alef
    assert fold_aware_contains("هذا", "هَٰذَا")               # defective
    assert fold_aware_contains("أتاكم", "أَتَىٰكُمْ")          # ىٰ digraph, plene
    assert fold_aware_contains("على", "عَلَىٰ")               # ىٰ digraph, word-final


def test_fold_contains_credits_word_boundary_compound():
    # Uthmani one-word يَـٰبُنَىَّ ↔ Imla'i two-word يَا بُنَيَّ, inside a verse, either answer style:
    assert fold_aware_contains("قال السعي يَا بُنَيَّ وقال", "يَـٰبُنَىَّ")   # Imla'i two-word answer
    assert fold_aware_contains("قال السعي يَـٰبُنَىَّ وقال", "يَـٰبُنَىَّ")   # Uthmani one-word answer


def test_fold_contains_is_direction_independent():
    # Spec requires equivalence in BOTH directions. The common case is Uthmani reference (QUL) vs an
    # Imla'i answer; the reverse (Imla'i reference ↔ Uthmani answer) must also hold — matched by also
    # trying the answer's plene (dagger→alef) form.
    assert fold_aware_contains("ٱلْكِتَٰبِ", "الكتاب")          # rev, plene long-ā
    assert fold_aware_contains("هَٰذَا", "هذا")                 # rev, defective long-ā
    assert fold_aware_contains("أَتَىٰكُمْ", "أتاكم")           # rev, ىٰ digraph
    assert fold_aware_contains("قال السعي يَـٰبُنَىَّ وقال", "يَا بُنَيَّ")  # rev, word boundary
    # per-position optionality handles a MIXED verse (defective هذا + plene الكتاب in one reference):
    assert fold_aware_contains("قال هذا الكتاب لقومه", "هَٰذَا ٱلْكِتَٰبَ")


def test_fold_contains_handles_multiline_reference():
    # A reference with a newline/tab (hadith chains in original-2026-10-21) must still take the fold
    # branch — the pattern builder collapses whitespace like normalize() does, so `\n` ≠ a required
    # literal newline the (space-collapsed) answer could never contain.
    assert fold_aware_contains("قال الكتاب سبحان ربنا", "ٱلْكِتَٰبِ\nسُبْحَٰنَ")
    assert fold_aware_contains("a the quick\tbrown fox", "quick brown")


def test_fold_contains_is_a_superset_of_bounded_contains():
    # strict superset ⇒ normalized=1 ⇒ contains=1 is preserved; the fold only adds credit
    for ans, exp in [
        ("In the beginning God created", "the beginning"),   # Latin, present
        ("ذلك الكتاب لا ريب فيه", "ذلك الكتاب"),               # Arabic, present
    ]:
        assert bounded_contains(ans, exp)
        assert fold_aware_contains(ans, exp)


# --- negatives: must stay word-bounded, script- and digit-safe -------------------------------


def test_fold_contains_negatives():
    assert not fold_aware_contains("", "ٱلْكِتَٰبِ")                  # empty reference (via answer="")
    assert not fold_aware_contains("ٱلْكِتَٰبِ", "")                  # empty reference
    assert not fold_aware_contains("Jude 1:30 says ...", "Jude 1:3")  # not 1:30 (bounded)
    assert not fold_aware_contains("وقال المهديون كلاما", "هدي")      # not a sub-word
    assert not fold_aware_contains("therapist notes", "the rapist")   # Latin, no ws flex
    assert not fold_aware_contains("الآية ١٣", "الآية ١ ٣")          # ١ ٣ ≠ ١٣ (digit separator)
    assert not fold_aware_contains("سورة ١٣", "سورة ١:٣")


# --- the fold runs AFTER NFKD (presentation forms decomposed first, then folded) -------------


def test_fold_applies_after_nfkd_decomposition():
    # U+FEEF = ALEF MAKSURA ISOLATED FORM; NFKD → U+0649, which the bare-maqsura fold turns to ya.
    assert unicodedata.normalize("NFKD", "ﻯ") == "ى"
    assert score_normalize("ﻯ") == score_normalize("ي")  # both → "ي"


# --- invariance: Latin byte-for-byte, Hebrew untouched by the Arabic rules -------------------


def test_latin_and_hebrew_invariant():
    for s in ("Hello, World!", "In the beginning God created the heavens.", "Jude 1:3", "café",
              "soft­hyphen", "“curly” ‘quotes’"):
        assert score_normalize(s) == normalize(s)        # the fold path leaves non-Arabic unchanged
        assert _answer_plene_form(s) == normalize(s)     # ...and so does the plene path
    heb = "בְּרֵאשִׁית בָּרָא אֱלֹהִים"
    assert score_normalize(heb) == normalize(heb)
    assert _answer_plene_form(heb) == normalize(heb)


# --- corpus collision diagnostic: the symmetric folds' distinct-word residue, pinned ----------

# The ACCEPTED distinct-word collision residue on the QUL corpus (Spec 52 known limitation,
# architect-approved). Each bucket merges words that are NOT the same word — they share a consonantal
# skeleton only after one of the fold rules. Computed over BOTH answer canonicalisations that
# `fold_aware_contains` tries (`score_normalize` = dagger-deleted, and `_answer_plene_form` = long-ā
# materialised), so it covers the optional-ā/plene branch too, not just the symmetric folds. Pinned at
# the STRICT-SKELETON level, so a NEW distinct word entering a bucket — or a new bucket — fails the
# test, while a harmless new spelling does not.
_ACCEPTED_DISTINCT_WORD_MERGES = {
    # hamza class (ء→ا)
    "سواا": {"سواء", "سوءا"},   # equal / evil
    "جزاا": {"جزاء", "جزءا"},   # recompense / a part
    "وراا": {"وراء", "ورءا"},   # behind / and he saw
    "ملا": {"ملء", "ملا"},      # fill / chiefs
    "شيا": {"شىء", "شيا"},      # thing / a thing (acc.)
    "بريا": {"برىء", "بريا"},   # free of / (acc.)
    # maqsura class (ى→ي)
    "نبي": {"نبى", "نبي"},      # prophet / inform!
    "قري": {"قرى", "قري"},      # towns / was recited
    "امري": {"امرى", "امري"},   # my affair / a man
    # optional-long-ā (plene) branch only
    "راا": {"راا", "رءا"},      # he saw (رَأَىٰ) / رَءَا
}


def _iter_texts(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("text", "text_uthmani", "text_imlaei", "verse", "content") and isinstance(v, str):
                yield v
            else:
                yield from _iter_texts(v)
    elif isinstance(obj, list):
        for x in obj:
            yield from _iter_texts(x)


def _strict_skeleton(w: str) -> str:
    # Fold ONLY the zero-risk orthography (dagger/digraph→alef, wasl, marks) but KEEP standalone hamza
    # ء and alef-maqsura ى distinct from ا/ي, so it SEES the collisions the fold rules introduce.
    s = unicodedata.normalize("NFKD", w)
    s = s.replace("ىٰ", "ا").replace("ٰ", "ا")  # ىٰ digraph + lone dagger → alef
    s = strip_script_marks(s)  # Mn marks + editorial (tatweel/annotation), wasl ٱ→ا
    return s.replace(" ", "")


def test_corpus_collision_diagnostic():
    words = {w for t in _iter_texts(json.loads(QUL.read_text(encoding="utf-8"))) for w in t.split()}
    assert len(words) > 10000  # sanity: the sweep actually read the corpus

    # Sweep BOTH answer canonicalisations that fold_aware_contains tries: the dagger-deleted
    # score_normalize AND the long-ā-materialised plene form — so the diagnostic covers the
    # optional-ā/plene branch, not only the symmetric folds. A distinct-word merge is a bucket whose
    # members today's normalize() keeps apart AND whose strict skeletons still differ.
    residue: dict[str, set[str]] = {}
    for form in (score_normalize, _answer_plene_form):
        buckets: dict[str, set[str]] = defaultdict(set)
        for w in words:
            k = form(w)
            if k:
                buckets[k].add(w)
        for k, v in buckets.items():
            if len(v) > 1 and len({normalize(w) for w in v}) > 1:
                skels = {_strict_skeleton(w) for w in v}
                if len(skels) > 1:
                    residue.setdefault(k, set()).update(skels)
    # Two-sided bound: a no-op fold yields 0 (lower bound catches it); an explosion signals a bad
    # rule (upper bound). Measured 10 (9 symmetric + 1 plene-only, راا).
    assert 4 < len(residue) < 40, f"distinct-word merge count {len(residue)} out of range"
    # The residue keys must be EXACTLY the pre-registered allow-list (new/vanished bucket fails):
    assert set(residue) == set(_ACCEPTED_DISTINCT_WORD_MERGES), (
        "distinct-word collision residue changed; new="
        f"{sorted(set(residue) - set(_ACCEPTED_DISTINCT_WORD_MERGES))} "
        f"gone={sorted(set(_ACCEPTED_DISTINCT_WORD_MERGES) - set(residue))}"
    )
    # ...and each bucket's distinct-skeleton SET must match the pin (a new distinct word in an
    # existing bucket, which would not change the key set, still fails):
    for k, skels in residue.items():
        assert skels == _ACCEPTED_DISTINCT_WORD_MERGES[k], (
            f"bucket {k!r} membership changed: {sorted(skels)} vs {sorted(_ACCEPTED_DISTINCT_WORD_MERGES[k])}"
        )
