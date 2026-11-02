| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| beam | 3% cov 100% (n=30; c/i/r 1/29/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 20% (n=30; c/i/r 0/6/24) | 67% cov 80% (n=30; c/i/r 16/8/6) | **19%** cov 75% (c/i/r 17/73/30) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| beam | Judaism | 3% cov 100% (n=30; c/i/r 1/29/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 20% (n=30; c/i/r 0/6/24) | 67% cov 80% (n=30; c/i/r 16/8/6) | **19%** cov 75% (n=120; c/i/r 17/73/30) |

### By text (one text = one work · version · language)

**beam**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 19% | 75% | 30 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| beam | 120 | 17,453 | 182,373 |
| **total** | 120 | 17,453 | 182,373 |
