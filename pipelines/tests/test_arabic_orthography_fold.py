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
    return score_normalize(a) == score_normalize(b) and score_normalize(b) == score_normalize(a)


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
    assert not arabic_ws_insensitive_contains("", uthmani)            # empty reference never matches


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


def test_corpus_collision_diagnostic():
    words = {w for t in _iter_texts(json.loads(QUL.read_text(encoding="utf-8"))) for w in t.split()}
    assert len(words) > 10000  # sanity: the sweep actually read the corpus

    new_buckets: dict[str, set[str]] = defaultdict(set)
    for w in words:
        nw = score_normalize(w)
        if nw:
            new_buckets[nw].add(w)

    # merges the NEW fold introduces that the CURRENT normalize kept apart
    introduced = [
        (k, v) for k, v in new_buckets.items()
        if len(v) > 1 and len({normalize(w) for w in v}) > 1
    ]
    # Bounded (measured ~65). A regression that explodes this is a signal to re-review the rules.
    assert len(introduced) < 150, f"introduced merges jumped to {len(introduced)} — re-review rules"

    # Every introduced merge must be between genuine orthographic variants — i.e. the raw words
    # coincide once the fold's OWN alphabet is neutralised to a bare consonantal skeleton. This
    # neutralises exactly what the fold neutralises (so a true variant-merge passes) while still
    # catching a bug that merged words differing in a real consonant (كتب vs كلب). The dagger and
    # the ىٰ digraph fold to alef here (NOT deleted), matching the fold — otherwise an Uthmani
    # dagger-form would look distinct from its plene spelling.
    def skeleton(w: str) -> str:
        s = unicodedata.normalize("NFKD", w)
        s = s.replace("ىٰ", "ا").replace("ٰ", "ا")  # ىٰ digraph and lone dagger → alef
        s = strip_script_marks(s)  # drop Mn marks + editorial (tatweel/annotation), fold wasl
        for a, b in (("ى", "ي"), ("ء", "ا"), ("آ", "ا"), ("أ", "ا"), ("إ", "ا")):
            s = s.replace(a, b)
        return s.replace(" ", "")

    for _, v in introduced:
        skels = {skeleton(w) for w in v}
        assert len(skels) == 1, f"fold merged non-variant words: {sorted(v)} (skeletons {skels})"
