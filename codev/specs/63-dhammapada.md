# Specification: Add the Dhammapada (Pali)

**Scope.** This spec adds the corpus. Scoring Pali correctly is a separate change. Until it lands,
`collect` and `score` refuse Pali rows, as they refuse Gurmukhi rows today (Spec 50).

## Problem Statement

The pool has no Buddhist text. The Dhammapada is a natural first one: a short, fixed text of 423
numbered verses, known across every Buddhist tradition.

## Nomenclature

| Term | Meaning |
|---|---|
| **Pali** | The language of the Theravada canon. It has no script of its own; each tradition writes it in local letters. |
| **Romanized Pali** | Pali in Latin letters with diacritics (`ā`, `ṃ`, `ṭ`). This is Pali, not a translation. |
| **Gāthā** | A verse. VRI marks its lines `gatha1`, `gatha2`, `gatha3`, `gathalast`. |
| **Vagga** | A chapter; the Dhammapada has 26. |
| **Uddāna** | A closing mnemonic summary of a book's contents. Not a verse of the text. |
| **Chaṭṭha Saṅgāyana** | The Sixth Council recension (Burma, 1954–56). |
| **Mahāsaṅgīti** | The Dhamma Society of Bangkok's edited version of that text, used by SuttaCentral. |

## Current State

- A text enters the pool when `language == canonical_language`, and gets 28 questions. An entry
  needs ≥12 words to be asked about, ≥16 for `complete_unit`.
- `normalize()` mangles romanized Pali. NFKD splits each diacritic off its letter, and the
  punctuation pass turns it into a space: `dhammā` == `dhamma`, and `manopubbaṅgamā` becomes
  `manopubban gama`.
- `collect` and `score` refuse `pa` rows through a canary. Nothing guards `pi`.

## Source

| Candidate | Terms | Verdict |
|---|---|---|
| **VRI** (`VipassanaTech/tipitaka-xml`, Chaṭṭha Saṅgāyana) | "freely available for non-commericial use", with attribution to VRI | **Chosen** |
| SuttaCentral Mahāsaṅgīti (`bilara-data`) | Pali public domain, but: "We politely request that our content not be scraped or used in any way for the creation of datasets for generative AI or similar." | Rejected: a benchmark of generative AI goes against this request |
| Digital Pali Reader, Myanmar set | 0BSD on the software | Rejected: the text is VRI's, a 2011 copy, word for word identical |
| Digital Pali Reader, Thai set | Same | Rejected: edition unnamed, verses unnumbered |

The non-commercial term matches the Talmud's CC-BY-NC, which the catalogue already marks `open`.

Facts measured on VRI at commit `2d134ff` (file SHA-256 `17bd8e40…`):

- `romn/s0502m.mul.xml`: UTF-16 TEI, 423 verses, 26 chapters. VRI captures its text in Devanagari
  and generates this file by script conversion.
- The verses carry apparatus: 191 `<note>` variant readings and `<pb>` page markers of other
  editions. After verse 423 come the closing summaries.
- Dhp 359 prints two stanzas, the first (`icchādosā`) in parentheses. SuttaCentral has only that
  first stanza.
- Against SuttaCentral's text, ignoring `ṁ`/`ṃ` and quote marks: 380 verses identical, 12 differ in
  word breaks only, 7 in nasal spelling only, and 24 in wording or other spelling.
- After conversion, 228 verses have ≥12 words and 43 have ≥16.

## Desired State

| Field | Value |
|---|---|
| Tradition directory / `tradition` | `Buddhism` / `[Buddhism]` |
| `work` / `version` | `Dhammapada` / `Chaṭṭha Saṅgāyana (VRI)` |
| `language` = `canonical_language` | `pi` |
| `document_type` / `license` | `scripture` / `open`, VRI's terms quoted in `license_detail` |
| `unit_type` | `verse` |
| Citation | `Dhammapada N`, the number VRI prints; generate shows it as "the Dhammapada 5" |
| `requested_as` | the Dhammapada, the Pali Dhammapada, the Dhammapadapāḷi |

- **Raw payload.** VRI's file, byte for byte, with commit and SHA-256 in `source.yaml`.
- **Entry text.** VRI's romanized words and punctuation, without notes, page markers or the
  parentheses. Closing summaries are not verses. Dhp 359 keeps both stanzas.
- **Canary.** `pi` joins the `collect` and `score` gates, keyed on `dhammā` == `dhamma`, and the
  gates open by themselves when `normalize()` keeps Pali diacritics apart. All `normalize()` script fixes
  (Gurmukhi, Devanagari, Pali) go in one branch, issue #50 part 2.

## Success Criteria

- [ ] The catalogue loads; the default pool is 19 texts.
- [ ] Convert yields 423 verses, `Dhammapada 1` to `Dhammapada 423`.
- [ ] A test over every verse shows the words are unchanged, and fails if one letter is dropped.
- [ ] Generate gives the Dhammapada 28 questions with no shortfall.
- [ ] `collect` and `score` refuse `pi` rows while the canary holds, and the test fails if the
      gate is removed.
- [ ] The committed 2026-10-21 FAccT card is unchanged.
- [ ] The regeneration anchor is re-pinned; the copyright audit passes.

## Constraints

- One converter and one registry line; no core pipeline change beyond the gate list.
- Generate's word thresholds stay.
- No re-run of `collect`, `score` or `generate` over committed run evidence.

## Open Questions

1. **Script.** Romanized text is the form scholarship uses, but it is VRI's conversion of its
   Devanagari master. **Decided: romanized.**
2. **Edition spelling.** An answer from a Mahāsaṅgīti-style edition writes `ṁ` for `ṃ`, and may
   differ in the 24 verses above. How far to credit another edition's reading is a scoring
   question. **Out of scope.**
3. **Same-language negatives.** No other `pi` text exists, so every `verify_source` negative is
   in another language, as with Sri Guru Granth Sahib (#29). **Out of scope.**

## Risks

| Risk | Mitigation |
|---|---|
| Non-commercial terms in a public repo | Accepted for this research benchmark; quoted in `source.yaml`; same class as the Talmud |
| VRI asks users to sync with its latest files | Commit and SHA pinned; a re-pin is a sanctioned corpus update |
| A note or marker leaks into a verse | Per-verse test over all 423, and fail-fast on unknown markup |
| Pali mis-scored | Canary gate |

## References

- VRI: https://github.com/VipassanaTech/tipitaka-xml (`2d134ff`)
- SuttaCentral licensing and methodology, `bilara-data@59b845a`, `root/en/site/`
- Spec 26 (original-language pool), Spec 50 (Sri Guru Granth Sahib, canary)
