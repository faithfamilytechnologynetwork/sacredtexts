| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| qwen3-32b | 44% cov 100% (n=9; c/i/r 4/5/0) | 0% cov 100% (n=9; c/i/r 0/9/0) | 0% cov 100% (n=9; c/i/r 0/9/0) | 89% cov 100% (n=9; c/i/r 8/1/0) | **33%** cov 100% (c/i/r 12/24/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| qwen3-32b | Christianity | 44% cov 100% (n=9; c/i/r 4/5/0) | 0% cov 100% (n=9; c/i/r 0/9/0) | 0% cov 100% (n=9; c/i/r 0/9/0) | 89% cov 100% (n=9; c/i/r 8/1/0) | **33%** cov 100% (n=36; c/i/r 12/24/0) |

### By text (one text = one work · version · language)

**qwen3-32b**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Bible (the Greek New Testament (Scrivener 1894), grc) | 36 | 33% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| qwen3-32b | 36 | 6,492 | 23,740 |
| **total** | 36 | 6,492 | 23,740 |
