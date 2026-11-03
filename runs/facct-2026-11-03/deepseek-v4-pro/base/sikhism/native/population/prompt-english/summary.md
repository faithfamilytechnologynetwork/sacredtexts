| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| deepseek-v4-pro | 3% cov 100% (n=30; c/i/r 1/29/0; minor/major 0/29) | 3% cov 100% (n=30; c/i/r 1/29/0; minor/major 1/28) | 0% cov 100% (n=25; c/i/r 0/25/0; minor/major 0/25) | 77% cov 100% (n=30; c/i/r 23/7/0; minor/major 0/7) | **22%** cov 100% (c/i/r 25/90/0; minor/major 1/89) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| deepseek-v4-pro | cite_passage | 29 | 0 | 29 | wrong_locus 29 |
| deepseek-v4-pro | complete_unit | 29 | 1 | 28 | wrong_passage 28, omission 1 |
| deepseek-v4-pro | retrieve_quote | 25 | 0 | 25 | wrong_passage 25 |
| deepseek-v4-pro | verify_source | 7 | 0 | 7 | wrong_verdict 7 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| deepseek-v4-pro | Sikhism | 3% cov 100% (n=30; c/i/r 1/29/0) | 3% cov 100% (n=30; c/i/r 1/29/0) | 0% cov 100% (n=25; c/i/r 0/25/0) | 77% cov 100% (n=30; c/i/r 23/7/0) | **22%** cov 100% (n=115; c/i/r 25/90/0) |

### By text (one text = one work · version · language)

**deepseek-v4-pro**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 115 | 22% | 100% | 0 | — | 1 | 89 | wrong_passage 53, omission 1, wrong_locus 29, wrong_verdict 7 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| deepseek-v4-pro | 115 | 13,880 | 1,637 |
| **total** | 115 | 13,880 | 1,637 |
