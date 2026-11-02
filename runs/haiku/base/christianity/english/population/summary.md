| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| haiku | 83% cov 100% (n=30; c/i/r 25/5/0) | 47% cov 50% (n=30; c/i/r 7/8/15) | 40% cov 33% (n=30; c/i/r 4/6/20) | 93% cov 97% (n=30; c/i/r 27/2/1) | **75%** cov 70% (c/i/r 63/21/36) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| haiku | Christianity | 83% cov 100% (n=30; c/i/r 25/5/0) | 47% cov 50% (n=30; c/i/r 7/8/15) | 40% cov 33% (n=30; c/i/r 4/6/20) | 93% cov 97% (n=30; c/i/r 27/2/1) | **75%** cov 70% (n=120; c/i/r 63/21/36) |

### By text (one text = one work · version · language)

**haiku**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Bible (NRSV, en) | 120 | 75% | 70% | 36 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| haiku | 120 | 9,707 | 7,268 |
| **total** | 120 | 9,707 | 7,268 |
