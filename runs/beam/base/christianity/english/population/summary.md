| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| beam | 100% cov 100% (n=30; c/i/r 30/0/0) | 83% cov 100% (n=30; c/i/r 25/5/0) | 73% cov 100% (n=30; c/i/r 22/8/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **89%** cov 100% (c/i/r 107/13/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| beam | Christianity | 100% cov 100% (n=30; c/i/r 30/0/0) | 83% cov 100% (n=30; c/i/r 25/5/0) | 73% cov 100% (n=30; c/i/r 22/8/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **89%** cov 100% (n=120; c/i/r 107/13/0) |

### By text (one text = one work · version · language)

**beam**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Bible (NRSV, en) | 120 | 89% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| beam | 120 | 11,702 | 46,324 |
| **total** | 120 | 11,702 | 46,324 |
