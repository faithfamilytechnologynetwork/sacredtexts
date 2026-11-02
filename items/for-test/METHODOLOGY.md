# Methodology

This is the sampling design for the test set in this folder. The headline
estimate and the familiarity check are different questions. Report them
separately. Do not average them into one accuracy.

## What is being estimated

The population sample estimates how a model handles a typical passage of a
work. The familiarity panel estimates how it handles lines that are widely
quoted and therefore likely to have been seen in training. Those lines are not
a random sample of the work. Mixing them into the headline would favor
traditions whose famous passages are over-represented in training data.

## Population sample

Thirty passages per tradition. The draw is uniform, seed `20261030`, from
passages of at least 16 words. Every citation in `well_known.yaml` is removed
before the draw, so a famous line cannot also occupy a population slot.

The full NRSV file is gitignored. The draw uses the Protestant verse list in
`kjv.json` to choose citations. The scored wording is the NRSV text of those
citations, in `christianity/english/population/questions.jsonl`.

## Familiarity panel

The panel is the whole list in `well_known.yaml` for that edition. It is not a
quarter of the draw, and it is not cut or padded so the traditions match. The
population draw is conditional on this pre-registered list: the familiar citations
are removed from the pool before the seeded draw, so changing the list re-draws the
population sample (seed fixed at 20261030).

| Tradition | Familiar passages |
|---|---|
| Christianity | 4 |
| Judaism | 1 |
| Islam | 8 |
| Sikhism | 3 |

Compare traditions on the population sample of 30. Report the familiarity
panel with its own count.

## Questions

Each passage is asked as four tasks: `retrieve_quote`, `complete_unit`,
`cite_passage`, and `verify_source`.

Christianity is one set of 30. The English edition is the NRSV. The same
citations are also asked in their original language: the Masoretic text
(Westminster Leningrad Codex) for Hebrew Bible verses, including the Aramaic
of Daniel 2, and the Greek New Testament (Scrivener 1894) for New Testament
verses. That is not a second sample of 30, and the Old Testament verses are
not also asked from the Septuagint. The licensed Greek Orthodox TLG files
are still not in the repo.

Judaism's Aramaic edition and its English edition are the same 30 citations.
The Aramaic edition is two calls: an English prompt and a native-language
prompt. The English edition is one call. Islam and Sikhism are the native
edition only, also as two calls. This corpus has no English Qur'an and no
English Guru Granth Sahib.

The prompt names the edition. A native edition is not asked in both languages
inside one prompt. The native-language lines are drafts for a native speaker.
The model call has no language field. OpenRouter does not add one.

The Qur'an's English prompts name the edition "the Uthmani Qur'an" and the Arabic
prompts "القرآن الكريم بالرسم العثماني" (no "QUL"); the catalogue `version`
("Uthmani (QUL)") is unchanged in each question's source metadata. The Arabic
wording was signed off by the Islam representative, a native speaker: "رسم" is
orthography, "طبعة" a print run, so "طبعة عثماني" was wrong; "النص" rather than
"الاقتباس" for revelation; "رقم السورة والآية" rather than "الاستشهاد" (which means
martyrdom / evidentiary citation); and a closing "فقط" because Arabic-prompted
models tend to open with a preamble (بسم الله…, قال تعالى:) or a clause before the
verdict, which the leading-stance parser scores as refused — a deliberate, small
asymmetry versus the English "Answer Yes or No". The verify `no` donors are hadith
(content negatives), so naming the orthography does not turn verify into a spelling
test.

`complete_unit` expects the remaining words of the passage. Continuing into
later verses is still correct: the headline treats the answer as correct when
those remaining words are contained in it. A `cite_passage` item that should
be declined because the quotation is from another edition is not in this run.

Within each sample, half of the `verify_source` questions quote a real passage
from a different work and expect `no`. The donor is the same language as the
edition in the question, and the nearest other work this corpus holds. A
familiarity list of one passage stays `yes`, because half of one rounds to zero.
`true_tradition` is a scorer label. The prompt only asks yes or no.

| Edition being asked | Donor for `no` | Why |
|---|---|---|
| Aramaic Talmud | Masoretic text | Hebrew or Aramaic that is not the Talmud. No Midrash is in the corpus |
| English Talmud | NRSV, Hebrew Bible verses only | The English Tanakh this corpus holds. New Testament verses are not the donor. No English Midrash is in the corpus |
| NRSV | Book of Mormon, 2013 edition | Another English scripture |
| Masoretic text | Aramaic Talmud | The other Hebrew-Aramaic work |
| Qur'an | A hadith from the six canonical collections (Bukhari, Muslim, Abu Dawud, Tirmidhi, Nasa'i, Ibn Majah) | Same script and same tradition as the Qur'an, a different work. The question is a real "Qur'an or hadith?" judgement, not an alphabet test (issue #75) |
| Greek New Testament, Guru Granth Sahib, Sanskrit Gita, Pali Dhammapada | A passage from another tradition | No second work in that language. The script differs, so these `no` items are easier |

The English Gita already uses other English works. The modern supplemental
pair swaps the Book of Mormon and the encyclicals.

The hadith donor is chosen by the script of the quoted passage, not by the
tradition: an Arabic passage gets a hadith, so an English Qur'an edition, if
one is added, would get an English donor. Four rules keep the hadith item a
fair "Qur'an or hadith?" question:

- **Sayings only** (owner-approved matn-only, quote-bounded). The quoted text
  is the span sunnah.com puts in quotation marks right after a salawat
  ("صلى الله عليه وسلم"), optionally with a speech verb between ("قَالَ",
  "يَقُولُ", "فَقَالَ", "أَنَّهُ قَالَ"), up to its closing mark. That is the
  Prophet's own words. The narrator chain (isnad) before it, and anything after
  the closing mark (a narrator's remark, a second chain, the compiler's
  commentary), are never quoted. sunnah.com's quotation marks and the
  right-to-left marks around them are not copied, so the prompt keeps exactly
  one pair of quotation marks. A hadith is not used when there is no such span,
  or when the span:
  - has fewer than 16 words;
  - opens with a narrator chain or a reported clause (حَدَّثَنَا, أَخْبَرَنَا,
    عَنْ, وَعَنْ, أَنَّ, …), which would announce "hadith" from its first word.
    "إِنَّ" ("indeed") is a normal opening and is kept;
  - reads as a bare verdict itself ("لاَ، …"), by the scorer's own yes/no
    reader;
  - carries God's speech ("قَالَ اللَّهُ", "يَقُولُ اللَّهُ", "إِنَّ اللَّهَ … قَالَ"):
    hadith qudsi are out, and so are Qur'an citations framed that way;
  - carries a salawat. The Qur'an never does, so it would announce "hadith".

  These rules leave 4,204 sayings across the six books. A speaking-verb rule
  without the closing mark was tried first; by eye it left 11 of 38 items
  starting mid-sentence or ending in a chain.
- **No Qur'an wording** (owner-raised). Hadith quote the Qur'an, so a donor
  could make a `no` item partly true. A hadith is skipped if it contains a
  whole ayah, lies inside one, or shares 6 consecutive words with one. The
  comparison is orthography-aware (Uthmani or Imla'i spelling, the scorer's
  `fold_aware_contains`). It is conservative: a matn that merely contains a
  one-word ayah such as "وَٱلْعَصْرِ" (103:1) or "ٱلرَّحْمَٰنُ" (55:1) is also
  skipped, as is one containing the word "أَلَمْ", which folds to "الٓمٓ" (2:1).
  On the committed draw it changed 1 of the 38 `no` items: Nasa'i 3573, whose
  "عَبْدُ الرَّحْمَنِ" contains the one-word ayah 55:1. The God's-speech rule above
  already removes most hadith that quote an ayah.
- **Curated skip list** (owner check). After reading every drawn donor, two
  hadith are skipped at draw time: Sahih al-Bukhari 6784, a reply cut from a
  longer hadith that also shares 5 words with 9:102 (one under the threshold),
  and Sahih al-Bukhari 7122, God's words ("إِنَّ رَحْمَتِي تَغْلِبُ غَضَبِي")
  without a "قَالَ اللَّهُ" frame. The list is `DONOR_SKIP` in
  `build_questions.py`, with a reason for each entry. Like the Qur'an-wording
  screen, it re-draws only the rows that drew a listed hadith.
- **Seeded per row.** Each Arabic row's hadith comes from its own RNG
  (seed 20261030, condition, sample, citation), so no other row or
  tradition can move it, and rebuilding Islam alone reproduces the full build.

The Qur'an `no` donors were re-drawn twice while these rules were settled
(PR #78 rounds 2 and 3). The skip list then re-drew two rows. Nothing had been
collected from any earlier draw.

## What to report

Report population accuracy on its own. Report familiarity accuracy on its own,
with the number of passages. Do not pool the two.

On `retrieve_quote` and `complete_unit`, read the two overlap scores together.
Neither one is the headline. `correct` still requires the passage, marks
included.

`token_f1` is the strict overlap. A vowel sign or a Latin accent is part of
the word, so `dhammā` is not `dhamma` and `café` is not `cafe`. Dropping a
Gurmukhi or Devanagari vowel sign, or a Pali length mark, misses that word.
Greek accents already fold, and Arabic and Hebrew vowel marks already fold,
so those pairs match on this score too.

`token_f1_base` is the same overlap after those Latin accents and Indic and
Pali vowel signs are removed. It answers a different question: did the words
change, or only the marks?

| Strict | Base | Reading |
|---|---|---|
| High | High | The same words, marks included |
| Low | High | The right words, with vowel signs or accents dropped |
| Low | Low | Different words. Treat this as a different passage |

A low strict score and a high base score is a spelling miss, not a theological
miss. A low score on both is a change of words.

Hinduism is the same 30 citations in both editions. The 16-word floor is
applied to Annie Besant's English, because only 16 Sanskrit verses reach 16
words. Buddhism is 30 Pali verses of at least 16 words. This corpus has no
English Dhammapada. Neither work has a familiarity list in `well_known.yaml`.

`christianity/modern/english/` is a separate modern sample: 15 Book of
Mormon verses (2013 edition) and 15 numbered paragraphs from the Vatican
English encyclicals. English only. It is not part of the population run and
is not averaged into the NRSV estimate.

## Models

Every run is search off, with no tools, through OpenRouter. The run artifacts
record the panel fingerprint: provider, model, and temperature.

Google's 4-series currently exposes only the argon tier on OpenRouter.
OpenAI's 6.1 generation has not yet refreshed its top and bottom tiers, so
astra and luna come from gpt-6.
