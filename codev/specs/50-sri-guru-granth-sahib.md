# Specification: Add Sri Guru Granth Sahib (Gurmukhi)

<!--
SPEC vs PLAN BOUNDARY:
This spec defines WHAT and WHY. The plan defines HOW and WHEN.
Keep implementation phases, file paths, code, and "first we will… then we will…"
out of the spec — those belong in codev/plans/50-*.md.
-->

**Scope.** This spec adds the corpus. Scoring Gurmukhi correctly is a separate change (part 2,
its own PR). Until it lands, no panel runs on Sri Guru Granth Sahib: today's `normalize()` deletes
Gurmukhi vowel signs, so `ਕਰਤਾ` and `ਕਰਤੀ` score as the same word.

## Problem Statement

The benchmark claims to be multi-faith by construction, but every text in the pool is Abrahamic.
No Sikh text is in it, and no Indic script. Sri Guru Granth Sahib is a natural first one: a fixed,
fully paginated text (1,430 Angs) with an openly licensed digital edition.

## Nomenclature

| Term | Meaning |
|---|---|
| **Ang** | A page of the standard 1,430-page saroop of Sri Guru Granth Sahib. Every edition shares this pagination, so the Ang is how Gurbani is cited. |
| **Pankti** | One line of Gurbani as a unit of the text: a verse line, a refrain or a heading. This is the benchmark's `unit_type`. |
| **Printed line** | A physical line on the printed Ang (Shabad OS's `line` field). It is **not** a pankti: several short panktis can share one printed line, and a long pankti can run over two. |
| **`Ang N:k`** | Our citation: the k-th pankti on Ang N, counted in reading order. k is a pankti count, not a printed-line number. |
| **Shabad** | A hymn: a group of panktis, often closed by a counter such as `॥੪॥੫॥`. |
| **Rahao** (`ਰਹਾਉ`) | "Pause": marks a shabad's central refrain. A word of the text, so it is kept. |
| **Vishraam** | Reading-pause marks (`; . ,`) that Shabad OS adds from a reading pothi. Not part of the text, so they are removed. |
| **Danda** (`।`, `॥`) | Verse-end punctuation. Removed from entry text: generate would count each one as a word. |
| **Gurmukhi** | The script of Sri Guru Granth Sahib. Its vowel signs (lagaan matra) are part of each word. |

## Current State

- A text enters the question pool when `language == canonical_language`. Each gets 28 questions
  from four templates. An entry needs ≥12 words to be asked about, ≥16 for `complete_unit`.
- `verify_source` negatives prefer a same-language passage from another family, then fall back to
  another language.
- A run's FAccT card is rebuilt from the live catalogue, so a text added after the run appears on
  it. With Sri Guru Granth Sahib catalogued, the 2026-10-21 card would list `pa` under
  `zero_question_languages`, though that run never saw it.

## Source

| Candidate | Licence | Bulk access | Verdict |
|---|---|---|---|
| **Shabad OS** (`shabados/shabados`) | Gurbani marked public domain (CC PDM 1.0), on condition that no word is added, deleted or altered. Code MIT. | One TOML file per line, in git | **Chosen** |
| BaniDB (Khalis Foundation) | Data terms unclear ("not completely open") | API only | Rejected |
| Sikher GurbaniDB | CC BY-NC-SA 3.0 | Old dump | Rejected: NC, superseded |

Facts measured on Shabad OS at commit `7e36a29` (2026-10-22):

- Sri Guru Granth Sahib is asset **SSA2** (Shabadaarth, SGPC): **60,555 lines, Angs 1–1430**. The
  whole database is 603 MB across many works.
- Each line has `page` (the Ang) and `line`, the **physical** printed line. Several panktis share a
  physical line, so `line` is not unique. Reading order is `sections → lineGroups → lines`.
- The text carries markup that is not in the printed Sri Guru Granth Sahib: vishraam marks
  `; . ,`, verse counters `॥੧॥`, a bindi + ZWJ + vowel order, variation selector U+FE00, and
  subscript digits in raag headings.
- **Two lines carry the wrong Ang.** JJSV (filed on 1337) belongs on 1336; V41B (filed on 1377)
  belongs on 1378. Both break reading order, and BaniDB places both on the corrected Ang.
- After cleaning, the median pankti has 6 words. 1,452 have ≥12 words; 100 have ≥16.

## Desired State

| Field | Value |
|---|---|
| Tradition directory / `tradition` | `Sikhism` / `[Sikhism]` |
| `work` / `version` | `Sri Guru Granth Sahib` / `Shabad OS (SGPC Shabadaarth)` |
| `language` = `canonical_language` | `pa` |
| `document_type` / `license` | `scripture` / `public-domain` |
| `unit_type` | `pankti`, for every line, headings included |
| Citation | `Ang N:k`, where k is the pankti's position on Ang N in reading order |
| `requested_as` | the Guru Granth Sahib, Sri Guru Granth Sahib, the Adi Granth, Sri Guru Granth Sahib Ji |

- **Raw payload.** A filtered extract of Shabad OS: every SSA2 line, its text exactly as stored, in
  reading order, with the upstream commit recorded. A committed script rebuilds it byte for byte.
- **Entry text.** The scripture without Shabad OS apparatus: drop vishraam marks, counters and
  dandas; restore standard vowel order; drop the variation selector and subscript digits. Keep
  `ਰਹਾਉ`, a word of the text. Dandas go because generate counts space-separated tokens as words.
- **No word is added, deleted or altered.** A test over every line proves the converter removes only
  the declared apparatus.
- **Ang errata** are corrected in the converter, never in the raw file. A correction that Shabad OS
  has since made fails convert loudly.
- **A run's card shows only texts that existed when the run was made.** Committed cards stay unchanged.

## Success Criteria

- [ ] The catalogue loads; the default pool is 18 texts.
- [ ] Convert yields 60,555 panktis across Angs 1–1430, with unique citations.
- [ ] The apparatus-only test passes over all of Sri Guru Granth Sahib, and fails if one vowel sign
      is dropped.
- [ ] Generate gives Sri Guru Granth Sahib 28 questions with no shortfall.
- [ ] The committed 2026-10-21 FAccT card is unchanged.
- [ ] The regeneration anchor is re-pinned per the 2026-10-28 procedure; the copyright audit passes.

## Constraints

- One converter and one registry line; no core pipeline change.
- Generate's word thresholds stay. Changing them would regenerate every text.
- No re-run of `collect`, `score` or `generate` over committed run evidence.

## Open Questions

1. **Citation precision.** People cite the Ang alone; few models will know `k`. Accept a low
   `cite_passage` ceiling for now, or score the Ang only (a scorer change)? **Recommend accept.**
2. **Repeated panktis.** 24 eligible texts repeat (the Mool Mantar 33 times), but `cite_passage`
   accepts one Ang. Generate never checks this for any text. **Recommend a separate change.**
3. **Same-script negatives.** Every negative for Sri Guru Granth Sahib is English, so trivially
   rejected (as in #29). Bhai Gurdas's Vaaran, in the same Shabad OS data, would give Gurmukhi ones.
   **Out of scope.**

## Risks

| Risk | Mitigation |
|---|---|
| A stripped character was part of a word | Apparatus-only test over all 60,555 lines |
| Shabad OS fixes or moves a line | Commit SHA pinned; stale errata fail loudly |
| `pa` simplifies a multilingual text (Sant Bhasha) | Noted in `source.yaml`; touches #27 |
| Gurmukhi mis-scored before part 2 lands | No panel until then; stated in the PR |

## References

- Shabad OS: https://github.com/shabados/shabados (`7e36a29`); licence statement in the archived
  https://github.com/shabados/database
- BaniDB API: https://github.com/KhalisFoundation/BaniDB-API
- Spec 26 (original-language pool), Spec 32 (FAccT card)
