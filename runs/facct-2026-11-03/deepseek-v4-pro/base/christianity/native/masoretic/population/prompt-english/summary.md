| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| deepseek-v4-pro | 90% cov 100% (n=21; c/i/r 19/2/0; minor/major 0/2) | 24% cov 100% (n=21; c/i/r 5/16/0; minor/major 11/5) | 71% cov 100% (n=21; c/i/r 15/6/0; minor/major 6/0) | 100% cov 100% (n=21; c/i/r 21/0/0; minor/major 0/0) | **71%** cov 100% (c/i/r 60/24/0; minor/major 17/7) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| deepseek-v4-pro | cite_passage | 2 | 0 | 2 | wrong_locus 1, no_citation 1 |
| deepseek-v4-pro | complete_unit | 16 | 11 | 5 | edition_variant 1, paraphrase 3, wrong_passage 5, omission 7 |
| deepseek-v4-pro | retrieve_quote | 6 | 6 | 0 | diacritic_only 1, edition_variant 1, near_copy 1, paraphrase 2, omission 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| deepseek-v4-pro | Christianity | 90% cov 100% (n=21; c/i/r 19/2/0) | 24% cov 100% (n=21; c/i/r 5/16/0) | 71% cov 100% (n=21; c/i/r 15/6/0) | 100% cov 100% (n=21; c/i/r 21/0/0) | **71%** cov 100% (n=84; c/i/r 60/24/0) |

### By text (one text = one work · version · language)

**deepseek-v4-pro**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 50% | 100% | 0 | — | 1 | 1 | paraphrase 1, wrong_passage 1 |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 72% | 100% | 0 | — | 16 | 6 | diacritic_only 1, edition_variant 2, near_copy 1, paraphrase 4, wrong_passage 4, omission 8, wrong_locus 1, no_citation 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| deepseek-v4-pro | 84 | 10,882 | 3,942 |
| **total** | 84 | 10,882 | 3,942 |
