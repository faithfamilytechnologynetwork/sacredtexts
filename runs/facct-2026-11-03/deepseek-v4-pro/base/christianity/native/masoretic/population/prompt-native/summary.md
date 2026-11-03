| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| deepseek-v4-pro | 100% cov 100% (n=21; c/i/r 21/0/0; minor/major 0/0) | 19% cov 100% (n=21; c/i/r 4/17/0; minor/major 11/6) | 67% cov 100% (n=21; c/i/r 14/7/0; minor/major 5/2) | 86% cov 100% (n=21; c/i/r 18/3/0; minor/major 0/3) | **68%** cov 100% (c/i/r 57/27/0; minor/major 16/11) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| deepseek-v4-pro | complete_unit | 17 | 11 | 6 | paraphrase 3, wrong_passage 6, omission 8 |
| deepseek-v4-pro | retrieve_quote | 7 | 5 | 2 | edition_variant 3, paraphrase 2, wrong_passage 2 |
| deepseek-v4-pro | verify_source | 3 | 0 | 3 | wrong_verdict 3 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| deepseek-v4-pro | Christianity | 100% cov 100% (n=21; c/i/r 21/0/0) | 19% cov 100% (n=21; c/i/r 4/17/0) | 67% cov 100% (n=21; c/i/r 14/7/0) | 86% cov 100% (n=21; c/i/r 18/3/0) | **68%** cov 100% (n=84; c/i/r 57/27/0) |

### By text (one text = one work · version · language)

**deepseek-v4-pro**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 50% | 100% | 0 | — | 1 | 1 | paraphrase 1, wrong_passage 1 |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 69% | 100% | 0 | — | 15 | 10 | edition_variant 3, paraphrase 4, wrong_passage 7, omission 8, wrong_verdict 3 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| deepseek-v4-pro | 84 | 9,565 | 4,038 |
| **total** | 84 | 9,565 | 4,038 |
