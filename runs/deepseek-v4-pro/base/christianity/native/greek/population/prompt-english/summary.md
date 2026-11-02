| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| deepseek-v4-pro | 0% cov 100% (n=9; c/i/r 0/9/0) | 78% cov 100% (n=9; c/i/r 7/2/0) | 22% cov 100% (n=9; c/i/r 2/7/0) | 100% cov 100% (n=9; c/i/r 9/0/0) | **50%** cov 100% (c/i/r 18/18/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| deepseek-v4-pro | Christianity | 0% cov 100% (n=9; c/i/r 0/9/0) | 78% cov 100% (n=9; c/i/r 7/2/0) | 22% cov 100% (n=9; c/i/r 2/7/0) | 100% cov 100% (n=9; c/i/r 9/0/0) | **50%** cov 100% (n=36; c/i/r 18/18/0) |

### By text (one text = one work · version · language)

**deepseek-v4-pro**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Bible (the Greek New Testament (Scrivener 1894), grc) | 36 | 50% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| deepseek-v4-pro | 36 | 3,593 | 1,075 |
| **total** | 36 | 3,593 | 1,075 |
