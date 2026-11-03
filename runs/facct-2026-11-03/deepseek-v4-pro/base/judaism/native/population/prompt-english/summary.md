| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| deepseek-v4-pro | 23% cov 100% (n=30; c/i/r 7/23/0; minor/major 0/23) | 3% cov 100% (n=30; c/i/r 1/29/0; minor/major 4/25) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 1/29) | 70% cov 100% (n=30; c/i/r 21/9/0; minor/major 0/9) | **24%** cov 100% (c/i/r 29/91/0; minor/major 5/86) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| deepseek-v4-pro | cite_passage | 23 | 0 | 23 | wrong_locus 10, no_citation 13 |
| deepseek-v4-pro | complete_unit | 29 | 4 | 25 | paraphrase 3, wrong_passage 25, omission 1 |
| deepseek-v4-pro | retrieve_quote | 30 | 1 | 29 | paraphrase 1, wrong_passage 14, other_script 15 |
| deepseek-v4-pro | verify_source | 9 | 0 | 9 | wrong_verdict 9 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| deepseek-v4-pro | Judaism | 23% cov 100% (n=30; c/i/r 7/23/0) | 3% cov 100% (n=30; c/i/r 1/29/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 70% cov 100% (n=30; c/i/r 21/9/0) | **24%** cov 100% (n=120; c/i/r 29/91/0) |

### By text (one text = one work · version · language)

**deepseek-v4-pro**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 24% | 100% | 0 | — | 5 | 86 | paraphrase 4, wrong_passage 39, other_script 15, omission 1, wrong_locus 10, no_citation 13, wrong_verdict 9 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| deepseek-v4-pro | 120 | 12,524 | 5,976 |
| **total** | 120 | 12,524 | 5,976 |
