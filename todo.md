# SacredBench — what is still open

The current run is a probe: 17 texts, three models. The agreed first corpus is not that probe.

## Corpus

- [ ] Masoretic Text (Hebrew), as its own text. The Judaism folder is the Talmud, not the Tanakh.
- [ ] Septuagint, as its own text. The Greek Orthodox catalogue names it. The payload is not in the questions.
- [ ] Greek New Testament (Novum Testamentum Graece), as its own text. Same gap.
- [ ] NRSV as the single English reference, only if the license allows. It is not in the index. Do not substitute KJV, ASV, or WEB.
- [ ] One text per tradition in the headline question file. Extra editions stay out of that file.

## Next run, or a check the stored files cannot finish

- [ ] Score the English Davidson Talmud against the Aramaic Talmud. Same work, two languages. The English edition is indexed and was excluded because its language is not the canonical one.
- [ ] Arabic instructions for the Arabic items. An English Qur'an only if the license allows.
- [ ] A second hadith numbering scheme for the citation task only. Quote, completion, and verification do not use that number, and the Qur'an to Bukhari gap is still there on the first two. Record whether gold is the isnad, the matn, or both.
- [ ] Near-copy counts by language. The letter fold is in `sacredbench probes` (7 of 158). The by-language table is not.
- [ ] Per-model accuracy inside each text. Question-clustered intervals are in `sacredbench probes`. The per-model rows are not.
- [ ] Decide whether the other-script answers should stay incorrect. 23 of 38 say they are unsure or ask for a number. The other 15 are English caveats too. Do not add untested Arabic decline phrases.
- [ ] Decoding parameters and system prompts are not in the run artifact. Record them on the next collect.
- [ ] License terms for the Qur'an source and the Latter-day Saint editions before any release of questions.
- [ ] An independent rater for the paraphrase band and for wrong citations. The author audit is not that rater.
