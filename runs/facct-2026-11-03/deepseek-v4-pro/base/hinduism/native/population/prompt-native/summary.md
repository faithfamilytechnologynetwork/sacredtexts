| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| deepseek-v4-pro | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | 17% cov 100% (n=30; c/i/r 5/25/0; minor/major 14/11) | 47% cov 100% (n=30; c/i/r 14/16/0; minor/major 7/9) | 87% cov 100% (n=30; c/i/r 26/4/0; minor/major 0/4) | **62%** cov 100% (c/i/r 74/46/0; minor/major 21/25) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| deepseek-v4-pro | cite_passage | 1 | 0 | 1 | no_citation 1 |
| deepseek-v4-pro | complete_unit | 25 | 14 | 11 | near_copy 1, paraphrase 7, wrong_passage 11, omission 6 |
| deepseek-v4-pro | retrieve_quote | 16 | 7 | 9 | paraphrase 7, wrong_passage 9, addition 14 |
| deepseek-v4-pro | verify_source | 4 | 0 | 4 | wrong_verdict 4 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| deepseek-v4-pro | Hinduism | 97% cov 100% (n=30; c/i/r 29/1/0) | 17% cov 100% (n=30; c/i/r 5/25/0) | 47% cov 100% (n=30; c/i/r 14/16/0) | 87% cov 100% (n=30; c/i/r 26/4/0) | **62%** cov 100% (n=120; c/i/r 74/46/0) |

### By text (one text = one work · version · language)

**deepseek-v4-pro**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 62% | 100% | 0 | — | 21 | 25 | near_copy 1, paraphrase 14, wrong_passage 20, omission 6, addition 14, no_citation 1, wrong_verdict 4 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| deepseek-v4-pro | 120 | 12,084 | 5,860 |
| **total** | 120 | 12,084 | 5,860 |
