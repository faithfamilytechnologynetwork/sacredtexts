| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemma-31b | 22% cov 100% (n=9; c/i/r 2/7/0) | 0% cov 100% (n=9; c/i/r 0/9/0) | 0% cov 100% (n=9; c/i/r 0/9/0) | 100% cov 100% (n=9; c/i/r 9/0/0) | **31%** cov 100% (c/i/r 11/25/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemma-31b | Christianity | 22% cov 100% (n=9; c/i/r 2/7/0) | 0% cov 100% (n=9; c/i/r 0/9/0) | 0% cov 100% (n=9; c/i/r 0/9/0) | 100% cov 100% (n=9; c/i/r 9/0/0) | **31%** cov 100% (n=36; c/i/r 11/25/0) |

### By text (one text = one work · version · language)

**gemma-31b**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Bible (the Greek New Testament (Scrivener 1894), grc) | 36 | 31% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemma-31b | 36 | 3,937 | 805 |
| **total** | 36 | 3,937 | 805 |
