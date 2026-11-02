| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| argon | 100% cov 100% (n=30; c/i/r 30/0/0) | 77% cov 100% (n=30; c/i/r 23/7/0) | 77% cov 100% (n=30; c/i/r 23/7/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **88%** cov 100% (c/i/r 106/14/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| argon | Christianity | 100% cov 100% (n=30; c/i/r 30/0/0) | 77% cov 100% (n=30; c/i/r 23/7/0) | 77% cov 100% (n=30; c/i/r 23/7/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **88%** cov 100% (n=120; c/i/r 106/14/0) |

### By text (one text = one work · version · language)

**argon**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Bible (NRSV, en) | 120 | 88% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| argon | 120 | 9,802 | 2,353 |
| **total** | 120 | 9,802 | 2,353 |
