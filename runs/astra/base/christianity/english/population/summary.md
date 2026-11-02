| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| astra | 100% cov 100% (n=30; c/i/r 30/0/0) | 0% cov 3% (n=30; c/i/r 0/1/29) | n/a cov 0% (n=30; c/i/r 0/0/30) | 100% cov 100% (n=30; c/i/r 30/0/0) | **98%** cov 51% (c/i/r 60/1/59) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| astra | Christianity | 100% cov 100% (n=30; c/i/r 30/0/0) | 0% cov 3% (n=30; c/i/r 0/1/29) | n/a cov 0% (n=30; c/i/r 0/0/30) | 100% cov 100% (n=30; c/i/r 30/0/0) | **98%** cov 51% (n=120; c/i/r 60/1/59) |

### By text (one text = one work · version · language)

**astra**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Bible (NRSV, en) | 120 | 98% | 51% | 59 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| astra | 120 | 6,891 | 5,319 |
| **total** | 120 | 6,891 | 5,319 |
