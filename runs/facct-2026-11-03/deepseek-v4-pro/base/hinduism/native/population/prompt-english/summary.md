| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| deepseek-v4-pro | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | 23% cov 100% (n=30; c/i/r 7/23/0; minor/major 14/9) | 37% cov 100% (n=30; c/i/r 11/19/0; minor/major 5/14) | 77% cov 100% (n=30; c/i/r 23/7/0; minor/major 0/7) | **58%** cov 100% (c/i/r 70/50/0; minor/major 19/31) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| deepseek-v4-pro | cite_passage | 1 | 0 | 1 | wrong_locus 1 |
| deepseek-v4-pro | complete_unit | 23 | 14 | 9 | diacritic_only 1, paraphrase 8, wrong_passage 9, omission 5 |
| deepseek-v4-pro | retrieve_quote | 19 | 5 | 14 | edition_variant 3, paraphrase 2, wrong_passage 14 |
| deepseek-v4-pro | verify_source | 7 | 0 | 7 | wrong_verdict 7 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| deepseek-v4-pro | Hinduism | 97% cov 100% (n=30; c/i/r 29/1/0) | 23% cov 100% (n=30; c/i/r 7/23/0) | 37% cov 100% (n=30; c/i/r 11/19/0) | 77% cov 100% (n=30; c/i/r 23/7/0) | **58%** cov 100% (n=120; c/i/r 70/50/0) |

### By text (one text = one work · version · language)

**deepseek-v4-pro**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 58% | 100% | 0 | — | 19 | 31 | diacritic_only 1, edition_variant 3, paraphrase 10, wrong_passage 23, omission 5, wrong_locus 1, wrong_verdict 7 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| deepseek-v4-pro | 120 | 12,554 | 2,387 |
| **total** | 120 | 12,554 | 2,387 |
