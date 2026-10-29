# FAccT benchmark card — original-2026-10-21

*What this benchmark run is allowed to mean — and what it is not.*

## The panel

The models behind the numbers, with any tools they were given — tool use is part of a model's identity here, so the same model with search on and off are different panellists.

| Model | Provider | Model ID | Tools | Endpoint |
| --- | --- | --- | --- | --- |
| gpt-oss-20b | openai | openai/gpt-oss-20b | none | openrouter.ai |
| haiku | openai | anthropic/claude-haiku-5-5 | none | openrouter.ai |
| opus | openai | anthropic/claude-opus-5-5 | none | openrouter.ai |

*Provider is the API protocol the run used, not the model's maker — an `anthropic/…` model reached over an OpenAI-compatible endpoint shows provider `openai`; read Model ID and Endpoint for the real source.*

## The tasks

Each question uses one of these tasks:

- **cite_passage** — name the citation a quoted passage comes from
- **complete_unit** — continue a verse or unit from its opening words
- **retrieve_quote** — quote a named edition's exact wording of a citation
- **verify_source** — judge whether a passage really is from a claimed source

## Who the questions represent

The questions are drawn from original-language editions only: a text is asked about just when the edition is in its own canonical language. The tables below are the make-up of the questions in this run — not a ranking of anyone's scripture, and not a measure of how well a model knows a faith.

This run asked **476 questions** across **17 texts**.

**By tradition**

| Tradition | Texts |
| --- | ---: |
| Judaism | 1 |
| Protestant Christian | 3 |
| Sunni Islam | 10 |
| The Church of Jesus Christ of Latter-Day Saints | 3 |

*A text shared by more than one tradition is counted under each, so these can total more than the number of texts.*

**The texts asked about**

| Text | Language | Tradition | Type | License |
| --- | --- | --- | --- | --- |
| Book of Mormon (2013 edition) | English (en) | The Church of Jesus Christ of Latter-Day Saints | scripture | open |
| Doctrine and Covenants (2013 edition) | English (en) | The Church of Jesus Christ of Latter-Day Saints | scripture | open |
| Jami` at-Tirmidhi (sunnah.com Arabic) | Arabic (ar) | Sunni Islam | hadith_collection | public-domain |
| Musnad Ahmad (sunnah.com Arabic) | Arabic (ar) | Sunni Islam | hadith_collection | public-domain |
| Muwatta Malik (sunnah.com Arabic) | Arabic (ar) | Sunni Islam | hadith_collection | public-domain |
| Pearl of Great Price (2013 edition) | English (en) | The Church of Jesus Christ of Latter-Day Saints | scripture | open |
| Sahih Muslim (sunnah.com Arabic) | Arabic (ar) | Sunni Islam | hadith_collection | public-domain |
| Sahih al-Bukhari (sunnah.com Arabic) | Arabic (ar) | Sunni Islam | hadith_collection | public-domain |
| Sunan Abi Dawud (sunnah.com Arabic) | Arabic (ar) | Sunni Islam | hadith_collection | public-domain |
| Sunan Ibn Majah (sunnah.com Arabic) | Arabic (ar) | Sunni Islam | hadith_collection | public-domain |
| Sunan al-Darimi (sunnah.com Arabic) | Arabic (ar) | Sunni Islam | hadith_collection | public-domain |
| Sunan an-Nasa'i (sunnah.com Arabic) | Arabic (ar) | Sunni Islam | hadith_collection | public-domain |
| Talmud Bavli (William Davidson Edition - Aramaic) | Hebrew (he) | Judaism | talmud | open |
| The Bible (ASV (1901)) | English (en) | Protestant Christian | scripture | public-domain |
| The Bible (KJV) | English (en) | Protestant Christian | scripture | public-domain |
| The Bible (WEB) | English (en) | Protestant Christian | scripture | public-domain |
| The Qur'an (Uthmani (QUL)) | Arabic (ar) | Sunni Islam | scripture | public-domain |

**Languages with zero questions:** Greek (grc), Latin (la). A language listed here is present in the catalogue but asked no questions in this run. It is a held-back or out-of-pool source, not a gap the models failed to cover.

**Excluded from the pool.** These texts are in the catalogue but outside this run's pool, each for the stated reason (an edition whose language is not its canonical language).

- Papal Encyclicals (Vatican English, en) — language 'en' != canonical_language 'la'
- Talmud Bavli (William Davidson Edition - English, en) — language 'en' != canonical_language 'he'

## What the models did

Each answer is one of three outcomes: correct, incorrect, or a refusal. A refusal — the model declining to answer — is neither right nor wrong, so it is set aside: accuracy counts only answered questions, and coverage is the share of questions that were answered. A high accuracy on low coverage is not mastery; read the two together.

What counts as correct depends on the task:

- **cite_passage** — the answer must name the one correct citation
- **complete_unit** — the continuation must *contain* the reference wording
- **retrieve_quote** — the answer must *contain* the requested edition's wording
- **verify_source** — the answer must give the correct leading Yes / No

For the two text-retrieval tasks, 'contain' is a word-bounded, script-aware match (graders: strict, containment) — not an exact string match — the same match the edition question below uses.

| Model | Task | Correct | Incorrect | Refused | Accuracy | Coverage |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| gpt-oss-20b | cite_passage | 1 | 116 | 2 | 0.9% | 98.3% |
| gpt-oss-20b | complete_unit | 0 | 52 | 67 | 0.0% | 43.7% |
| gpt-oss-20b | retrieve_quote | 0 | 32 | 87 | 0.0% | 26.9% |
| gpt-oss-20b | verify_source | 63 | 56 | 0 | 52.9% | 100.0% |
| gpt-oss-20b | **overall** | 64 | 256 | 156 | **20.0%** | **67.2%** |
| haiku | cite_passage | 33 | 68 | 18 | 32.7% | 84.9% |
| haiku | complete_unit | 25 | 82 | 12 | 23.4% | 89.9% |
| haiku | retrieve_quote | 14 | 25 | 80 | 35.9% | 32.8% |
| haiku | verify_source | 113 | 6 | 0 | 95.0% | 100.0% |
| haiku | **overall** | 185 | 181 | 110 | **50.5%** | **76.9%** |
| opus | cite_passage | 54 | 63 | 2 | 46.2% | 98.3% |
| opus | complete_unit | 69 | 40 | 10 | 63.3% | 91.6% |
| opus | retrieve_quote | 47 | 16 | 56 | 74.6% | 52.9% |
| opus | verify_source | 118 | 1 | 0 | 99.2% | 100.0% |
| opus | **overall** | 288 | 120 | 68 | **70.6%** | **85.7%** |

## Would another edition have passed?

3 of the texts are different editions of the same Bible (ASV (1901), KJV, WEB). When a model was asked for one edition's wording of a verse and missed, it sometimes answered with a faithful wording of the *same verse from a different edition*. The count below is how many of those misses were really another edition of the right verse.

| Model | Another edition would have passed | Of incorrect Bible retrieve_quote |
| --- | ---: | ---: |
| gpt-oss-20b | 0 | 17 |
| haiku | 3 | 15 |
| opus | 0 | 0 |

A model shown 0 of 0 had no incorrect Bible retrieve_quote answers to reconsider.

*Scope: Bible retrieve_quote cells only. complete_unit is excluded (its gold is a partial unit with no well-defined sibling-edition segment); the 3 Bible editions (ASV (1901), KJV, WEB) are the only sibling editions in the pool, and non-Bible citations (Arabic surah:ayah, hadith numbers, Talmud daf:line) are never matched to a Bible edition.*

## What this card claims

- For this panel, on these original-language editions, the accuracy-with-coverage figures above are how often each model succeeded at each task — quoting the requested wording, completing a unit, naming a citation, or judging a source — with refusals set aside.
- Some Bible misses are edition mismatches, not wrong verses; the edition count says how many.

## What would make this card wrong

- If the scoring contract behind these outcomes changed and the card were not rebuilt from the new scores, every number here would be stale.
- If a citation were matched to an edition it does not belong to, the edition count would be inflated; the count is computed for Bible verse citations only, for exactly this reason.

## What this card does not conclude

- It does not rank traditions and does not measure knowledge of any faith.
- A tradition's row is the slice that was asked — which may be a hadith collection or an English-language question set — not that community's whole scripture.
- The edition count is reported for the English Bible editions only; the other texts have no second indexed edition in this run, so the question does not arise for them.

## Community review

Scholar and community review of this card is not attached. The card reports what the run measured; it is not an adjudication by any tradition.
