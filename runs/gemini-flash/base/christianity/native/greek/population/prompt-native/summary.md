| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemini-flash | 100% cov 100% (n=9; c/i/r 9/0/0) | 100% cov 100% (n=9; c/i/r 9/0/0) | 89% cov 100% (n=9; c/i/r 8/1/0) | 100% cov 100% (n=9; c/i/r 9/0/0) | **97%** cov 100% (c/i/r 35/1/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemini-flash | Christianity | 100% cov 100% (n=9; c/i/r 9/0/0) | 100% cov 100% (n=9; c/i/r 9/0/0) | 89% cov 100% (n=9; c/i/r 8/1/0) | 100% cov 100% (n=9; c/i/r 9/0/0) | **97%** cov 100% (n=36; c/i/r 35/1/0) |

### By text (one text = one work · version · language)

**gemini-flash**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Bible (the Greek New Testament (Scrivener 1894), grc) | 36 | 97% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemini-flash | 36 | 3,480 | 18,901 |
| **total** | 36 | 3,480 | 18,901 |
