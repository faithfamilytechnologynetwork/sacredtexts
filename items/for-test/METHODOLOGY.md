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

Christianity has no NRSV file in `texts/raw`. The draw uses the Protestant
verse list in `kjv.json` to choose citations. The scored wording is the NRSV
text of those citations, in `christianity/english/population/questions.jsonl`.

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

Christianity is already English, so each passage is one question per task.
Judaism is asked twice, because the Aramaic Davidson edition and the English
Davidson edition are different wording. Islam and Sikhism are asked once.
This corpus has no English Qur'an and no English Guru Granth Sahib.

The prompt names the edition. For a non-English text it also states the
question in that text's language. Those second-language lines are drafts for
a native speaker. The model call has no language field. OpenRouter does not
add one.

Within each sample, half of the `verify_source` questions quote a real passage
from a different tradition and expect `no`. A familiarity list of one passage
stays `yes`, because half of one rounds to zero.

## What to report

Report population accuracy on its own. Report familiarity accuracy on its own,
with the number of passages. Do not pool the two. Hinduism and Buddhism are
not in this set: the Bhagavad Gita and the Dhammapada are not in `texts/raw`.

## Models

Every run is search off, with no tools, through OpenRouter. The run artifacts
record the panel fingerprint: provider, model, and temperature.

Google's 4-series currently exposes only the argon tier on OpenRouter.
OpenAI's 6.1 generation has not yet refreshed its top and bottom tiers, so
astra and luna come from gpt-6.
