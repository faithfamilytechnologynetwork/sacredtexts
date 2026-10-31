# Specification: Score Gurmukhi, Devanagari and romanized Pali correctly

**Scope.** Issue #50 part 2. This spec changes scoring. It stacks on the Dhammapada (#63) and the
Bhagavad Gita (#64), and it opens their gates and Sri Guru Granth Sahib's.

## Problem Statement

`normalize()` runs NFKD, then turns everything that is not `\w` or whitespace into a space. Three
scripts break:

| Input | Today | Why it is wrong |
|---|---|---|
| `ਕਰਤਾ`, `ਕਰਤੀ` | both `ਕਰਤ` | Two words become one |
| `कर्मण्येवाधिकारस्ते` | `कर मण य व ध क रस त` | One word becomes eight |
| `manopubbaṅgamā` | `manopubban gama` | The word splits |

`collect` and `score` refuse `pa`, `sa` and `pi` rows until this is fixed.

## Nomenclature

| Term | Meaning |
|---|---|
| **Vowel sign** | A dependent vowel, category Mn or Mc. It is part of the spelling, unlike Arabic harakat. |
| **Danda** | `।` and `॥`, the Indic full stops. They stay separators. |
| **Pali letters** | `ā ī ū ṃ ṁ ṅ ñ ṭ ḍ ṇ ḷ`. NFKD splits each into a base letter and a mark. |
| **Pali reference** | A reference holding at least one Pali letter. |

## Design

1. **Indic marks stay in the word.** The punctuation pass exempts category M in the Devanagari and
   Gurmukhi blocks. Word edges treat those marks as word characters, so `ਕਰਤ` is not a word within
   `ਕਰਤਾ`. Native digits fold to ASCII, and a joiner after an Indic letter is dropped.
2. **Pali diacritics fold, scoped by the reference.** When the reference is Pali, both sides drop the
   diacritics straight after NFKD, so words stay whole and `dhammā` equals `dhamma`. `ṁ` and `ṃ`
   meet at `m`. `exact` stays strict. Otherwise nothing changes.
3. **`failure_kind` and the viewer follow the Indic rule,** with a shared parity fixture.

The gates stay in place. Their canaries now pass, so the gates are open, and they close again if
`normalize()` regresses.

## Why the Pali rule is scoped

Pali is Latin script, so an unscoped rule reaches English answers. It moved three `token_f1`
values in `original-2026-10-21`, in answers naming al-Bukhārī. No verdict flipped, but committed
evidence would have had to change. Scoping by the reference follows Spec 52, which kept the shared
`normalize()` stable and put its fold in the comparison.

## Success Criteria

- [ ] All three inputs above stay whole, across all 60,555 panktis, 700 verses and 423 verses.
- [ ] `dhammā` and `dhamma` score the same against a Pali reference; `exact` still tells them apart.
- [ ] Every metric of all 2,620 committed answers is unchanged, pinned by a hash from the pre-fix scorer.
- [ ] `gated_languages()` is empty.
- [ ] `naïve café résumé` keeps its pinned output.
- [ ] Python and the viewer agree on the parity fixture.
- [ ] The regeneration anchor is re-pinned if the question digest moves.

## Constraints

- `normalize()` with default arguments changes only inside the Indic blocks.
- No committed run is re-scored or edited.

## Open Questions

1. **Credit for an ASCII Pali answer?** Yes, the same points. Pali diacritics are a transliteration
   detail, so Pali follows the Arabic and Hebrew rule, not the Gurmukhi one: unmarked text scores the
   same, and some distinct words merge, as they do in unvocalised Arabic. A Gurmukhi vowel sign is
   the only way to write that vowel, so it stays. `exact` keeps the strict view.
2. **Other editions' readings.** An answer from another edition can differ in a word. **Out of scope.**
3. **A Sanskrit answer in IAST.** It is another script, so it does not match. **Out of scope.**

## Risks

| Risk | Mitigation |
|---|---|
| A Latin text moves | Witness hash over all committed answers; pinned Latin tests |
| The Python and TypeScript tokenizers drift | Shared fixture |
| A non-Pali reference holds a Pali letter | It gets the Pali rule on both sides; no committed reference does |
| A Pali reference holds no Pali letter | It gets the plain rule; none of the 14 generated references does |

## References

- Issue #50, Spec 50, Spec 52, Spec 63, Spec 64
- `pipelines/tests/test_script_normalize_rebaseline.py`
