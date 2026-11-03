| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| deepseek-v4-pro | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | 20% cov 100% (n=30; c/i/r 6/24/0; minor/major 15/9) | 30% cov 100% (n=30; c/i/r 9/21/0; minor/major 7/14) | 77% cov 100% (n=30; c/i/r 23/7/0; minor/major 0/7) | **56%** cov 100% (c/i/r 67/53/0; minor/major 22/31) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| deepseek-v4-pro | cite_passage | 1 | 0 | 1 | wrong_locus 1 |
| deepseek-v4-pro | complete_unit | 24 | 15 | 9 | diacritic_only 1, edition_variant 1, paraphrase 8, wrong_passage 9, omission 5 |
| deepseek-v4-pro | retrieve_quote | 21 | 7 | 14 | edition_variant 5, paraphrase 2, wrong_passage 14 |
| deepseek-v4-pro | verify_source | 7 | 0 | 7 | wrong_verdict 7 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| deepseek-v4-pro | Hinduism | 97% cov 100% (n=30; c/i/r 29/1/0) | 20% cov 100% (n=30; c/i/r 6/24/0) | 30% cov 100% (n=30; c/i/r 9/21/0) | 77% cov 100% (n=30; c/i/r 23/7/0) | **56%** cov 100% (n=120; c/i/r 67/53/0) |

### By text (one text = one work · version · language)

**deepseek-v4-pro**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 56% | 100% | 0 | — | 22 | 31 | diacritic_only 1, edition_variant 6, paraphrase 10, wrong_passage 23, omission 5, wrong_locus 1, wrong_verdict 7 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| deepseek-v4-pro | 120 | 12,554 | 2,387 |
| **total** | 120 | 12,554 | 2,387 |
