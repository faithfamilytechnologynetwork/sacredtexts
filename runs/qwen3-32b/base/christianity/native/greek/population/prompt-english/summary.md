| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| qwen3-32b | 11% cov 100% (n=9; c/i/r 1/8/0) | 0% cov 100% (n=9; c/i/r 0/9/0) | 0% cov 100% (n=9; c/i/r 0/9/0) | 100% cov 89% (n=9; c/i/r 8/0/1) | **26%** cov 97% (c/i/r 9/26/1) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| qwen3-32b | Christianity | 11% cov 100% (n=9; c/i/r 1/8/0) | 0% cov 100% (n=9; c/i/r 0/9/0) | 0% cov 100% (n=9; c/i/r 0/9/0) | 100% cov 89% (n=9; c/i/r 8/0/1) | **26%** cov 97% (n=36; c/i/r 9/26/1) |

### By text (one text = one work · version · language)

**qwen3-32b**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Bible (the Greek New Testament (Scrivener 1894), grc) | 36 | 26% | 97% | 1 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| qwen3-32b | 36 | 4,727 | 21,079 |
| **total** | 36 | 4,727 | 21,079 |
