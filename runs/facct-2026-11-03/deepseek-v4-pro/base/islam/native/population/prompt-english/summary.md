| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| deepseek-v4-pro | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | 53% cov 100% (n=30; c/i/r 16/14/0; minor/major 13/1) | 77% cov 100% (n=30; c/i/r 23/7/0; minor/major 2/5) | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | **81%** cov 100% (c/i/r 97/23/0; minor/major 15/8) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| deepseek-v4-pro | cite_passage | 1 | 0 | 1 | wrong_locus 1 |
| deepseek-v4-pro | complete_unit | 14 | 13 | 1 | paraphrase 2, wrong_passage 1, omission 11 |
| deepseek-v4-pro | retrieve_quote | 7 | 2 | 5 | edition_variant 1, near_copy 1, wrong_passage 5 |
| deepseek-v4-pro | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| deepseek-v4-pro | Islam | 97% cov 100% (n=30; c/i/r 29/1/0) | 53% cov 100% (n=30; c/i/r 16/14/0) | 77% cov 100% (n=30; c/i/r 23/7/0) | 97% cov 100% (n=30; c/i/r 29/1/0) | **81%** cov 100% (n=120; c/i/r 97/23/0) |

### By text (one text = one work · version · language)

**deepseek-v4-pro**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Qur'an (Uthmani (QUL), ar) | 120 | 81% | 100% | 0 | — | 15 | 8 | edition_variant 1, near_copy 1, paraphrase 2, wrong_passage 6, omission 11, wrong_locus 1, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| deepseek-v4-pro | 120 | 17,910 | 6,655 |
| **total** | 120 | 17,910 | 6,655 |
