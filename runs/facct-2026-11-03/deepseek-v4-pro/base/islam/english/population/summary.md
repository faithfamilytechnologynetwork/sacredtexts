| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| deepseek-v4-pro | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 47% cov 100% (n=30; c/i/r 14/16/0; minor/major 11/5) | 23% cov 100% (n=30; c/i/r 7/23/0; minor/major 10/13) | 87% cov 100% (n=30; c/i/r 26/4/0; minor/major 0/4) | **64%** cov 100% (c/i/r 77/43/0; minor/major 21/22) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| deepseek-v4-pro | complete_unit | 16 | 11 | 5 | edition_variant 1, paraphrase 5, wrong_passage 5, omission 5 |
| deepseek-v4-pro | retrieve_quote | 23 | 10 | 13 | edition_variant 4, near_copy 5, paraphrase 1, wrong_passage 13 |
| deepseek-v4-pro | verify_source | 4 | 0 | 4 | wrong_verdict 4 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| deepseek-v4-pro | Islam | 100% cov 100% (n=30; c/i/r 30/0/0) | 47% cov 100% (n=30; c/i/r 14/16/0) | 23% cov 100% (n=30; c/i/r 7/23/0) | 87% cov 100% (n=30; c/i/r 26/4/0) | **64%** cov 100% (n=120; c/i/r 77/43/0) |

### By text (one text = one work · version · language)

**deepseek-v4-pro**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Qur'an (Saheeh International (QUL), en) | 120 | 64% | 100% | 0 | — | 21 | 22 | edition_variant 5, near_copy 5, paraphrase 6, wrong_passage 18, omission 5, wrong_verdict 4 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| deepseek-v4-pro | 120 | 9,108 | 2,607 |
| **total** | 120 | 9,108 | 2,607 |
