| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| deepseek-v4-pro | 17% cov 100% (n=30; c/i/r 5/25/0; minor/major 0/25) | 3% cov 100% (n=30; c/i/r 1/29/0; minor/major 5/24) | 3% cov 100% (n=30; c/i/r 1/29/0; minor/major 0/29) | 77% cov 100% (n=30; c/i/r 23/7/0; minor/major 0/7) | **25%** cov 100% (c/i/r 30/90/0; minor/major 5/85) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| deepseek-v4-pro | cite_passage | 25 | 0 | 25 | wrong_locus 25 |
| deepseek-v4-pro | complete_unit | 29 | 5 | 24 | paraphrase 3, wrong_passage 24, omission 2 |
| deepseek-v4-pro | retrieve_quote | 29 | 0 | 29 | wrong_passage 29, addition 1 |
| deepseek-v4-pro | verify_source | 7 | 0 | 7 | wrong_verdict 7 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| deepseek-v4-pro | Judaism | 17% cov 100% (n=30; c/i/r 5/25/0) | 3% cov 100% (n=30; c/i/r 1/29/0) | 3% cov 100% (n=30; c/i/r 1/29/0) | 77% cov 100% (n=30; c/i/r 23/7/0) | **25%** cov 100% (n=120; c/i/r 30/90/0) |

### By text (one text = one work · version · language)

**deepseek-v4-pro**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 25% | 100% | 0 | — | 5 | 85 | paraphrase 3, wrong_passage 53, omission 2, addition 1, wrong_locus 25, wrong_verdict 7 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| deepseek-v4-pro | 120 | 11,176 | 4,567 |
| **total** | 120 | 11,176 | 4,567 |
