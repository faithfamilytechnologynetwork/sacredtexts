| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| deepseek-v4-pro | 78% cov 100% (n=9; c/i/r 7/2/0) | 67% cov 100% (n=9; c/i/r 6/3/0) | 67% cov 100% (n=9; c/i/r 6/3/0) | 89% cov 100% (n=9; c/i/r 8/1/0) | **75%** cov 100% (c/i/r 27/9/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| deepseek-v4-pro | Christianity | 78% cov 100% (n=9; c/i/r 7/2/0) | 67% cov 100% (n=9; c/i/r 6/3/0) | 67% cov 100% (n=9; c/i/r 6/3/0) | 89% cov 100% (n=9; c/i/r 8/1/0) | **75%** cov 100% (n=36; c/i/r 27/9/0) |

### By text (one text = one work · version · language)

**deepseek-v4-pro**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Bible (the Greek New Testament (Scrivener 1894), grc) | 36 | 75% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| deepseek-v4-pro | 36 | 4,046 | 1,114 |
| **total** | 36 | 4,046 | 1,114 |
