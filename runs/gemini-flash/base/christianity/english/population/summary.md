| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemini-flash | 100% cov 100% (n=30; c/i/r 30/0/0) | 60% cov 33% (n=30; c/i/r 6/4/20) | 83% cov 100% (n=30; c/i/r 25/5/0) | 97% cov 100% (n=30; c/i/r 29/1/0) | **90%** cov 83% (c/i/r 90/10/20) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemini-flash | Christianity | 100% cov 100% (n=30; c/i/r 30/0/0) | 60% cov 33% (n=30; c/i/r 6/4/20) | 83% cov 100% (n=30; c/i/r 25/5/0) | 97% cov 100% (n=30; c/i/r 29/1/0) | **90%** cov 83% (n=120; c/i/r 90/10/20) |

### By text (one text = one work · version · language)

**gemini-flash**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Bible (NRSV, en) | 120 | 90% | 83% | 20 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemini-flash | 120 | 6,223 | 72,213 |
| **total** | 120 | 6,223 | 72,213 |
