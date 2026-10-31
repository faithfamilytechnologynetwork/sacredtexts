# Specification: Add the Bhagavad Gita (Sanskrit)

**Scope.** This spec adds the corpus. Scoring Devanagari correctly is issue #50 part 2. Until it
lands, `collect` and `score` refuse `sa` rows: today's `normalize()` turns vowel signs and viramas
into spaces, so `कर्मण्येवाधिकारस्ते` becomes `कर मण य व ध क रस त`.

## Problem Statement

The pool has no Hindu text. The Bhagavad Gita is the natural first one: a fixed text of 18
chapters, cited by chapter and verse in every tradition that reads it.

## Nomenclature

| Term | Meaning |
|---|---|
| **Śloka** | A verse. This is the benchmark's `verse` unit. |
| **Mūlam** | The root text, without commentary or translation. |
| **Vulgate** | The Gita as transmitted through Śaṅkara's commentary and printed by Gita Press: 700 verses. |
| **Critical edition** | Belvalkar's text in the BORI Mahābhārata, 6.23–40. Also 700 verses, with different readings. |
| **`C:V`** | Our citation: chapter and verse, in Gita Press numbering. |
| **ZWNJ, ZWJ** | Invisible characters that steer how a conjunct is drawn. Not letters. |

## Source

| Candidate | Named edition | Licence | Verdict |
|---|---|---|---|
| **Stotra Samhita** (`stotrasamhita/gita`) | Credits the Śaṅkara Bhāṣya and the Gita Press padaccheda | No licence file | **Chosen** |
| `gita/gita` | None | Unlicense | Rejected: no edition, encoding defects, typos |
| BORI critical edition (GRETIL) | Yes | © BORI 1999, "for reference purposes only" | Local collation only, never committed |
| Besant/Natesan 1922 (Wikisource) | Yes, with scan | Public-domain book; contributions CC BY-SA | Not chosen |
| sanskritdocuments.org | None | Personal study and research | Rejected |

### Licence: for the reviewer to judge

**Stotra Samhita has no licence file.** The target is `license: open`, as the CC-BY-NC Talmud is,
with the facts quoted in `license_detail`. The case for committing it:

- The Gita is ancient and public domain.
- The extract holds only the verses, transcribed faithfully. A faithful transcription arguably adds
  no copyright, at least in the US (Feist, Bridgeman). Rights in editorial work may differ in India,
  the UK and the EU.
- The repository's one usage line, "For Personal Use Only / Not For Commercial Printing/Distribution",
  is commented out of `frontmatter.tex`. So it is neither in force nor a grant.

The case against: nobody has given written permission, and this benchmark is a non-commercial
research use, not a licence. The author can be asked; a grant would replace this reasoning.

### Measured on `b89199c` (2026-10-22)

- `gita.tex`, 700 numbered verses. The Gita Press chapter counts hold in all 18 chapters.
- The extra verse "prakṛtiṃ puruṣaṃ caiva…" is commented out as `13-0`, and upstream's own chapter 13
  comments run 13-2..13-35. Gita Press numbers that chapter 13.1–13.34.
- Verses 1.21 and 1.28 are split by a speaker line and set as two half-verses.
- 18 ZWNJ and ZWJ characters, and one `{\mbox{}न्न}` line-break guard (5.8).
- Median verse 10 words; 152 have ≥12 words, 16 have ≥16.

### Translation

| Candidate | Verse-aligned | Licence | Verdict |
|---|---|---|---|
| **Annie Besant, 1922** (G. A. Natesan; English Wikisource) | Yes, `(N)` after each verse | Public domain | **Chosen** |
| Telang, 1882 (*Sacred Books of the East* 8) | No: continuous prose, no verse numbers | Public domain | Rejected: splitting it would be our own judgement |
| Arnold, 1885 | No: verse poetry | Public domain | Rejected |
| `gita/gita` `translation.json` | Yes | Mostly modern translators | Rejected |
| `iddev5/bhagavad-gita-besant` | Yes, but merges three verses and shifts numbers | Public domain | Cross-check only |

Besant's was a popular translation with a Theosophical slant, not a scholarly one. It sits beside
the Sanskrit for reference and is not benchmarked. Measured on revisions current at 2026-10-30:

- 701 verses, numbered as printed, with the extra verse as 13.1.
- 686 of 701 verses match `iddev5/bhagavad-gita-besant` word for word. The other 15 are its typos,
  its three merged verses, and one heading it caught in ours (fixed).
- Eight English verse markers are misprinted: six flagged by the transcribers, and 17.19 and 18.14,
  confirmed against the adjacent Devanagari numbers.

## Desired State

| Field | Value |
|---|---|
| Tradition directory / `tradition` | `Hinduism` / `[Hinduism]` |
| `work` / `version` | `Bhagavad Gita` / `Stotra Samhita (Gita Press text)` |
| `language` = `canonical_language` | `sa` |
| `document_type` / `license` | `scripture` / `open` |
| `unit_type` | `verse` |
| Citation | `C:V`, Gita Press numbering. Bare, as the Qur'an's `2:255`: the scorer then credits `2:47`, `Bhagavad Gita 2:47` and `BG 2.47` |
| `requested_as` | the Bhagavad Gita, the Gita, the Bhagavad Gītā, the Srimad Bhagavad Gita |

- **Raw payload.** Verses only, each half-verse exactly as stored, with the upstream commit and
  SHA-256 recorded. A committed script rebuilds it byte for byte.
- **Entry text.** Half-verses joined by a space, without the `\mbox` guard or ZWNJ/ZWJ. No speaker
  lines, chapter titles or colophons.
- **Translation target.** Same `work`, `version: Annie Besant (1922)`, `language: en`,
  `canonical_language: sa`, `license: public-domain`. It is outside the pool, as the Talmud's English
  is. It shares the Sanskrit's citations; Besant's 13.1 is set aside, leaving 700 entries.
- **Canary.** `collect` and `score` refuse `sa` rows while `normalize()` collapses Devanagari.

## Success Criteria

- [ ] The catalogue loads; `Bhagavad Gita` is in the default pool.
- [ ] Convert yields 700 verses with unique citations, 13:1..13:34 included.
- [ ] A test over all 700 verses proves only the declared apparatus is removed.
- [ ] Besant's 700 entries carry exactly the Sanskrit's citations, with no leftover markup.
- [ ] Generate gives the Gita 28 questions with no shortfall.
- [ ] The canary test covers `sa` and fails if the gate is removed.
- [ ] The committed 2026-10-21 FAccT card is unchanged.
- [ ] The regeneration anchor is re-pinned; the copyright audit passes.

## Constraints

- One converter and one registry line.
- Generate's word thresholds stay.
- No re-run of `collect`, `score` or `generate` over committed run evidence.
- The BORI text is never committed.

## Open Questions

1. **Vulgate or critical edition?** Scholars cite the critical edition, and most readers know the
   vulgate. Models were likely trained on the vulgate. **Recommend the vulgate; report collation counts.**
2. **Same-script negatives.** No other `sa` text exists, so every negative is cross-language and
   trivially rejected, as in #29. **Out of scope.**
3. **Repeated verses.** Some half-verses recur. `cite_passage` accepts one citation, as with Sri Guru
   Granth Sahib. **Separate change.**

## Risks

| Risk | Mitigation |
|---|---|
| The author objects to redistribution | Stated in the PR; undo is one revert |
| A stripped character is part of a word | Apparatus-only test over all 700 verses |
| Stotra Samhita changes | Commit and SHA-256 pinned |
| Devanagari mis-scored before part 2 lands | Canary gates `sa` |
| Merge conflict with the Dhammapada PR | Same gate table and anchor; this PR rebases after it |

## References

- Stotra Samhita: https://github.com/stotrasamhita/gita (`b89199c`)
- GRETIL critical edition: https://gretil.sub.uni-goettingen.de/gretil/1_sanskr/2_epic/mbh/ext/bhgce__u.htm
- Spec 26 (original-language pool), Spec 50 (Sri Guru Granth Sahib)
