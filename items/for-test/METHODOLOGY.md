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
quarter of the draw, and it is not cut or padded so the traditions match.

| Tradition | Familiar passages |
|---|---|
| Christianity | 4 |
| Judaism | 1 |
| Islam | 7 |
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
| Greek New Testament, Qur'an, Guru Granth Sahib, Sanskrit Gita, Pali Dhammapada | A passage from another tradition | No second work in that language. The script differs, so these `no` items are easier |

The English Gita already uses other English works. The modern supplemental
pair swaps the Book of Mormon and the encyclicals.

## What to report

Report population accuracy on its own. Report familiarity accuracy on its own,
with the number of passages. Do not pool the two.

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
