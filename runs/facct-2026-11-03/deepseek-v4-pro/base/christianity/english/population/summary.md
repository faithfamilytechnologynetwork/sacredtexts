| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| deepseek-v4-pro | 90% cov 100% (n=30; c/i/r 27/3/0; minor/major 0/3) | 67% cov 100% (n=30; c/i/r 20/10/0; minor/major 6/4) | 83% cov 100% (n=30; c/i/r 25/5/0; minor/major 5/0) | 90% cov 100% (n=30; c/i/r 27/3/0; minor/major 0/3) | **82%** cov 100% (c/i/r 99/21/0; minor/major 11/10) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| deepseek-v4-pro | cite_passage | 3 | 0 | 3 | wrong_locus 3 |
| deepseek-v4-pro | complete_unit | 10 | 6 | 4 | edition_variant 2, near_copy 2, wrong_passage 4, omission 2, addition 1 |
| deepseek-v4-pro | retrieve_quote | 5 | 5 | 0 | edition_variant 1, near_copy 1, paraphrase 3 |
| deepseek-v4-pro | verify_source | 3 | 0 | 3 | wrong_verdict 3 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| deepseek-v4-pro | Christianity | 90% cov 100% (n=30; c/i/r 27/3/0) | 67% cov 100% (n=30; c/i/r 20/10/0) | 83% cov 100% (n=30; c/i/r 25/5/0) | 90% cov 100% (n=30; c/i/r 27/3/0) | **82%** cov 100% (n=120; c/i/r 99/21/0) |

### By text (one text = one work · version · language)

**deepseek-v4-pro**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (NRSV, en) | 120 | 82% | 100% | 0 | — | 11 | 10 | edition_variant 3, near_copy 3, paraphrase 3, wrong_passage 4, omission 2, addition 1, wrong_locus 3, wrong_verdict 3 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| deepseek-v4-pro | 120 | 6,613 | 1,824 |
| **total** | 120 | 6,613 | 1,824 |
