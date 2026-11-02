| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sonnet | 90% cov 100% (n=30; c/i/r 27/3/0) | 77% cov 100% (n=30; c/i/r 23/7/0) | 79% cov 63% (n=30; c/i/r 15/4/11) | 80% cov 83% (n=30; c/i/r 20/5/5) | **82%** cov 87% (c/i/r 85/19/16) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sonnet | Christianity | 90% cov 100% (n=30; c/i/r 27/3/0) | 77% cov 100% (n=30; c/i/r 23/7/0) | 79% cov 63% (n=30; c/i/r 15/4/11) | 80% cov 83% (n=30; c/i/r 20/5/5) | **82%** cov 87% (n=120; c/i/r 85/19/16) |

### By text (one text = one work · version · language)

**sonnet**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Bible (NRSV, en) | 120 | 82% | 87% | 16 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sonnet | 120 | 9,947 | 13,238 |
| **total** | 120 | 9,947 | 13,238 |
