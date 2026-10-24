# SacredBench — what is still open

The current run is a probe: 17 texts, three models, failure kinds. The agreed first corpus is not that probe. Do not treat the probe as the headline corpus until that run exists.

## Texts the first corpus still lacks

Agreed authoritative Christian sources, not yet the gold of the reported run:

- [ ] Masoretic Text (Hebrew). The Judaism folder is the William Davidson Talmud (Aramaic and English), not the Tanakh.
- [ ] Septuagint. A Greek Orthodox `source.yaml` names Septuagint and Greek New Testament (TLG). It is not in the probe questions.
- [ ] Greek New Testament (Novum Testamentum Graece). Same gap.
- [ ] One English reference only: NRSV, including deuterocanonical books so Protestant, Catholic, and Greek Orthodox canons are not three translations. NRSV is not in the index. KJV, ASV, and WEB are, and they are appendix material.

Present, but not the agreed Christian sample:

- [x] Protestant: keep KJV, ASV (1901), and WEB in the appendix. They are public domain, not the first corpus.
- [x] Roman Catholic: say the folder is papal encyclicals (English) plus a held-back NABRE. Encyclicals are not a Catholic Bible. NABRE is not the agreed English reference.
- [x] Latter-day Saint: Book of Mormon, Doctrine and Covenants, Pearl of Great Price (2013). Leave them as their own texts, not as “the Bible.”

Present and closer to the original-language rule:

- [x] Sunni Islam: the Uthmani Qur’an is the headline text. Keep the nine Arabic hadith collections as separate texts or appendix rows. Ten Sunni texts in one mean is the mistake Figure 1 is about.
- [x] Judaism: the probe text is the Aramaic Talmud only. The English Davidson edition is in the catalogue and was not the probe text. Say that.

Not in the tree at all (the old draft named them; this checkout does not):

- [x] Sikh sources. Not in this checkout. Do not claim them. The paper says they are absent.
- [x] Hindu texts. Do not claim them. The paper now says they are absent.
- [x] Buddhist texts. Do not claim them. The paper now says they are absent.

## Pipeline, before another model run

- [ ] Ingest Masoretic, Septuagint, and Greek New Testament as their own texts (work, version, language). Do not score them through an English file.
- [x] Add NRSV only if the license allows. It is not in the index. The paper says the English reference is missing and does not substitute KJV. The file itself is not added.
- [ ] One text per tradition in the headline question file. Extra editions stay out of that file.
- [x] Refusal cues are English. A Greek or Hebrew decline will be scored as a wrong answer. Stated in `outcomes.py` and in the paper. The cue list was not extended with untested phrases.
- [x] Author audit of the label rules on the whole class, not a second rater. 46 of 84 “paraphrase” cells have token overlap at least 0.85 (often the same Arabic verse). All 38 “wrong witness” cells are Latin-script answers, usually an English refusal. Citation labels match the strings on spot checks. A community rater is still missing.
- [x] Pre-register the 0.4 overlap cutoff and the eight-token addition bar, or treat the sensitivity table as the result and not a settled threshold. The paper takes the second option.
- [x] Take the paper’s counts from `sacredbench.failure_kind.report_run` on the stored run, not from a hand copy off the leaderboard.
