# SacredBench — what is still open

The agreed first corpus has not been run, so the evaluation is still a pilot.

## Corpus

- [ ] Masoretic Text (Hebrew), as its own text. The Judaism folder is the Talmud, not the Tanakh.
- [ ] Septuagint, as its own text. The Greek Orthodox catalogue names it. The payload is not in the questions.
- [ ] Greek New Testament (Novum Testamentum Graece), as its own text. Same gap.
- [ ] NRSV as the single English reference, only if the license allows. It is not in the index. Do not substitute KJV, ASV, or WEB.
- [ ] One text per tradition in the headline question file. Extra editions stay out of that file.
- [ ] Refusal cues in Hebrew and Greek once those witnesses are in the questions.

## Next run, or a check the stored files cannot finish

- [ ] Score the English Davidson Talmud against the Aramaic Talmud. Same work, two languages. The English edition is indexed and was excluded because its language is not the canonical one.
- [ ] Arabic instructions for the Arabic items, on a subset, so prompt language is not the same thing as text language. An English Qur'an only if the license allows.
- [ ] A second hadith numbering scheme for the citation task only. Quote, completion, and verification do not use that number. `sacredbench splits` reports the Fisher test: together the Qur'an is 12 of 31 and Bukhari is 3 of 25 (p about 0.03). Per task, and per model, the same test does not clear 0.05. Record whether gold is the isnad, the matn, or both.
- [x] Near-copy counts by language. `sacredbench splits` prints them (Arabic 26, English 19, Aramaic 1 on this run). The letter fold stays in `sacredbench probes` (7 of 158).
- [x] Per-model accuracy inside each text. `sacredbench splits` prints the table. Pooled accuracy still mixes models that refuse at different rates. gpt-oss-20b grades 17 of 28 on the Qur'an and 18 of 28 on Bukhari.
- [x] Refusals per text, not as an Arabic pool. `sacredbench splits` prints them. Of 248 Arabic refusals, 237 are hadith and 11 are the Qur'an. All 11 Qur'an refusals are gpt-oss-20b. Haiku and Opus refuse none of the Qur'an items. gpt-oss-20b refuses 12 of 84 English Bible answers (4 of 28 on each of KJV, ASV, and WEB).
- [ ] Revisit the refusal rule. 23 of 38 other-script answers say the model is unsure or ask for a number, and the other 15 are English caveats, but a leading-cue detector scores them incorrect. Do not add untested Arabic decline phrases. An independent rater on a sample has to decide which of those are refusals.
- [ ] Decoding parameters and system prompts are not in the run artifact. Record them on the next collect, including gpt-oss reasoning effort.
- [ ] License terms for the Qur'an source and the Latter-day Saint editions before any release of questions.
- [ ] An independent rater for the paraphrase band, for wrong citations, and for the other-script rows. The author audit is not that rater.
