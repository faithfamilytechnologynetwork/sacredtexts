"""Arabic orthography fold (Spec 52) — the position-aware Uthmani↔Imla'i equivalence that
`score_normalize` adds on top of `normalize`, plus the whitespace-insensitive containment helper.

These exercise the NEW capability in isolation (Phase 1): the fold is NOT yet wired into the
default scoring path, so `normalize()` and every committed score stay byte-identical (guarded by
the existing regression suites). Everything here is read-only; the corpus sweep reads the committed
open-licensed QUL Qur'an.
"""
from __future__ import annotations

import json
import unicodedata
from collections import defaultdict
from pathlib import Path

from sacredbench.score import (
    arabic_ws_insensitive_contains,
    fold_arabic_orthography,
    normalize,
    score_normalize,
    strip_script_marks,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
QUL = REPO_ROOT / "texts" / "raw" / "Sunni Islam" / "quran_uthmani_from_qul.json.json"


# --- the in-scope orthographic pairs fold equal, in both directions --------------------------


def _folds_equal(a: str, b: str) -> bool:
    # score_normalize is a pure function and string equality is symmetric, so one comparison
    # suffices; direction-independence has teeth only for the containment predicate (tested below).
    return score_normalize(a) == score_normalize(b)


def test_dagger_alef_folds_to_full_alef():
    # dagger-alif ↔ full alef (no word-boundary difference in this pair)
    assert _folds_equal("ذَٰلِكَ", "ذالك")


def test_medial_digraph_folds_to_alef():
    # ىٰ spelling long ā, medial (a letter follows) → ا
    assert _folds_equal("أَتَىٰكُمْ", "أَتَاكُمْ")
    assert score_normalize("أَتَىٰكُمْ") == "اتاكم"


def test_word_final_maqsura_and_digraph_fold_to_ya():
    # bare alef-maqsura, and the word-FINAL digraph, both → dotted ya
    assert _folds_equal("هدى", "هدي")
    assert _folds_equal("عَلَىٰ", "على")
    assert score_normalize("عَلَىٰ") == "علي"


def test_standalone_hamza_folds_to_alef():
    # أَرَءَيْتُمْ (standalone ء) ↔ أَرَأَيْتُمْ (seated hamza) — "drop" would be asymmetric
    assert _folds_equal("أَرَءَيْتُمْ", "أَرَأَيْتُمْ")
    assert score_normalize("أَرَءَيْتُمْ") == "ارايتم"


def test_already_folded_cases_still_fold():
    # NFKD + existing mark deletion already handle these; score_normalize must not regress them
    assert _folds_equal("آمن", "امن")          # alif madda
    assert _folds_equal("ٱلله", "الله")         # hamzat al-wasl
    assert _folds_equal("مؤمن", "مومن")         # hamza-on-waw
    # and the fold matches the base normalize() on an already-foldable Arabic pair
    assert normalize("آمن") == score_normalize("آمن")


# --- context dependence: the ىٰ rule must NOT be context-free --------------------------------


def test_digraph_is_position_aware_not_context_free():
    # medial → ا, final → ya; the two must both hold at once (no single char-map does this)
    assert score_normalize("أَتَىٰكُمْ") == "اتاكم"   # medial
    assert score_normalize("عَلَىٰ") == "علي"          # final


def test_stacked_marks_after_final_maqsura_stay_final():
    # وَعَلَىٰٓ = ...ى + dagger(U+0670) + madda(U+0653), then boundary. A naive "next char is a
    # letter ⇒ medial" check would read the trailing madda as a letter and fold to وعلا, breaking
    # the عَلَىٰ↔على invariant. The mark-skipping detector keeps it word-final → وعلي.
    assert score_normalize("وَعَلَىٰٓ") == "وعلي"
    assert score_normalize("وَعَلَىٰٓ") == score_normalize("وعلى")
    assert "وعلا" != score_normalize("وَعَلَىٰٓ")


# --- word-level collisions the fold MUST NOT create ------------------------------------------


def test_distinct_words_do_not_collide():
    assert score_normalize("قَالَ") != score_normalize("قِيلَ")   # qāla vs qīla
    assert score_normalize("بَيْت") != score_normalize("بَات")    # bayt vs bāt


# --- the fold runs AFTER NFKD (presentation forms are decomposed first, then folded) ---------


def test_fold_applies_after_nfkd_decomposition():
    # U+FEEF = ARABIC LETTER ALEF MAKSURA ISOLATED FORM; NFKD decomposes it to U+0649, which the
    # fold then turns into ya. Proves the ordering is NFKD → fold (not fold → NFKD, which would miss it).
    assert unicodedata.normalize("NFKD", "ﻯ") == "ى"
    assert score_normalize("ﻯ") == score_normalize("ي")  # both → "ي"


# --- word boundary via the whitespace-insensitive containment helper -------------------------


def test_word_boundary_contains_helper():
    # Uthmani one-word يَـٰبُنَىَّ vs Imla'i two-word يَا بُنَيَّ: equal only with whitespace ignored
    uthmani, imlaei = "يَـٰبُنَىَّ", "يَا بُنَيَّ"
    assert score_normalize(uthmani) != score_normalize(imlaei)        # a space remains
    assert arabic_ws_insensitive_contains(imlaei, uthmani)            # but contained either way
    assert arabic_ws_insensitive_contains(uthmani, imlaei)
    assert not arabic_ws_insensitive_contains(uthmani, "")            # empty reference never matches


def test_word_boundary_contains_is_bounded_and_script_gated():
    # Must stay word-bounded (the property bounded_contains guarantees) even with whitespace flex:
    assert not arabic_ws_insensitive_contains("Jude 1:30 says ...", "Jude 1:3")   # not 1:30
    assert not arabic_ws_insensitive_contains("وقال المهديون كلاما", "هدي")        # not sub-word
    # A real Arabic reference IS credited when present across the word boundary (full containment):
    assert arabic_ws_insensitive_contains("قال السعي يَـٰبُنَىَّ وقال", "يَا بُنَيَّ")
    # Non-Arabic reference: plain word-bounded containment, no whitespace flexing (Latin contract):
    assert arabic_ws_insensitive_contains("the beginning of wisdom", "beginning of")
    assert not arabic_ws_insensitive_contains("therapist notes", "the rapist")


# --- invariance: Latin byte-for-byte, Hebrew untouched by the Arabic rules -------------------


def test_latin_byte_invariant():
    for s in ("Hello, World!", "In the beginning God created the heavens.", "Jude 1:3", "café"):
        assert score_normalize(s) == normalize(s)
    # fold_arabic_orthography itself is a no-op on Latin
    assert fold_arabic_orthography("Hello") == "Hello"


def test_hebrew_untouched_by_arabic_rules():
    # a vocalised Hebrew string: score_normalize must equal normalize (no Arabic rule reaches it)
    heb = "בְּרֵאשִׁית בָּרָא אֱלֹהִים"
    assert score_normalize(heb) == normalize(heb)


# --- corpus diagnostic (Phase 1): enumerate introduced merges, prove they are bounded and are
#     orthographic variants, and that the control pairs never merge. NOT a zero-collision gate —
#     the dagger fix itself correctly reunites Uthmani dagger-forms with their plene spellings. --


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


# The ACCEPTED distinct-word collision residue on the QUL corpus (Spec 52 known limitation,
# architect-approved). Each `score_normalize` bucket below merges words that are NOT the same word
# — they share a consonantal skeleton only after the maqsura→ya or standalone-hamza→alef rule. This
# is pre-registered so (a) Phase 2 hand-verifies exactly these when a committed cell touches one and
# (b) any NEW distinct-word collision a future rule change introduces fails the test. Annotated:
_ACCEPTED_DISTINCT_WORD_MERGES = {
    # hamza class (ء→ا): the two members differ by a real standalone hamza
    "سواا": "سواء (equal) / سوء (evil)",
    "جزاا": "جزاء (recompense) / جزء (a part)",
    "وراا": "وراء (behind) / ورءا (and he saw)",
    "ملا": "ملأ (chiefs) / ملء (fill)",
    "شيا": "شىء (thing) / شيـٔا (a thing, acc.)",
    "بريا": "برىء (free of) / بريـٔا (acc.)",
    # maqsura class (ى→ي): dotless-ya word ↔ a genuinely different ya/hamza word
    "نبي": "نبى (prophet) / نبّئ (inform!)",
    "قري": "قرى (towns) / قرئ (was recited)",
    "امري": "أمرى (my affair) / امرئ (a man)",
}


def test_corpus_collision_diagnostic():
    words = {w for t in _iter_texts(json.loads(QUL.read_text(encoding="utf-8"))) for w in t.split()}
    assert len(words) > 10000  # sanity: the sweep actually read the corpus

    new_buckets: dict[str, set[str]] = defaultdict(set)
    for w in words:
        nw = score_normalize(w)
        if nw:
            new_buckets[nw].add(w)

    # merges the NEW fold introduces that the CURRENT normalize kept apart
    introduced = {
        k: v for k, v in new_buckets.items()
        if len(v) > 1 and len({normalize(w) for w in v}) > 1
    }
    # Two-sided bound: a no-op fold would yield 0 (lower bound catches it); an explosion signals a
    # bad rule (upper bound). Measured 65.
    assert 40 < len(introduced) < 120, f"introduced merge count {len(introduced)} out of range"

    # A STRICT skeleton that folds ONLY the zero-risk orthography (dagger/digraph→alef, wasl, marks,
    # NFKD hamza-seats/madda) but KEEPS standalone hamza ء and alef-maqsura ى distinct from ا/ي — so
    # it can SEE the collisions the fold's own alphabet would hide. Buckets whose members still
    # differ under this skeleton are genuine distinct-word merges.
    def strict_skeleton(w: str) -> str:
        s = unicodedata.normalize("NFKD", w)
        s = s.replace("ىٰ", "ا").replace("ٰ", "ا")  # ىٰ digraph + lone dagger → alef
        s = strip_script_marks(s)  # Mn marks + editorial (tatweel/annotation), wasl ٱ→ا
        return s.replace(" ", "")

    distinct_word_merges = {
        k for k, v in introduced.items() if len({strict_skeleton(w) for w in v}) > 1
    }
    # The distinct-word residue must be EXACTLY the pre-registered, hand-annotated allow-list — a
    # new collision (or a disappeared one) fails here and forces a re-review + architect sight.
    assert distinct_word_merges == set(_ACCEPTED_DISTINCT_WORD_MERGES), (
        "distinct-word collision residue changed; new="
        f"{sorted(distinct_word_merges - set(_ACCEPTED_DISTINCT_WORD_MERGES))} "
        f"gone={sorted(set(_ACCEPTED_DISTINCT_WORD_MERGES) - distinct_word_merges)}"
    )

    # Everything NOT in the residue is a pure same-word Uthmani↔plene reunion (zero-risk).
    for k, v in introduced.items():
        if k not in distinct_word_merges:
            assert len({strict_skeleton(w) for w in v}) == 1, (
                f"unexpected non-variant merge outside the allow-list: {sorted(v)}"
            )
