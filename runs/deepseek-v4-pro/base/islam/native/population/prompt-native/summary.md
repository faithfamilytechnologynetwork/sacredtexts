| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| deepseek-v4-pro | 63% cov 100% (n=30; c/i/r 19/11/0) | 60% cov 100% (n=30; c/i/r 18/12/0) | 3% cov 100% (n=30; c/i/r 1/29/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **57%** cov 100% (c/i/r 68/52/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| deepseek-v4-pro | Islam | 63% cov 100% (n=30; c/i/r 19/11/0) | 60% cov 100% (n=30; c/i/r 18/12/0) | 3% cov 100% (n=30; c/i/r 1/29/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **57%** cov 100% (n=120; c/i/r 68/52/0) |

### By text (one text = one work · version · language)

**deepseek-v4-pro**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Qur'an (Uthmani (QUL), ar) | 120 | 57% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| deepseek-v4-pro | 120 | 16,979 | 5,432 |
| **total** | 120 | 16,979 | 5,432 |
