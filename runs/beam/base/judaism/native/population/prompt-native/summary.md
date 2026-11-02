| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| beam | 10% cov 100% (n=30; c/i/r 3/27/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 90% cov 100% (n=30; c/i/r 27/3/0) | **25%** cov 100% (c/i/r 30/90/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| beam | Judaism | 10% cov 100% (n=30; c/i/r 3/27/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 90% cov 100% (n=30; c/i/r 27/3/0) | **25%** cov 100% (n=120; c/i/r 30/90/0) |

### By text (one text = one work · version · language)

**beam**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 25% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| beam | 120 | 16,895 | 135,793 |
| **total** | 120 | 16,895 | 135,793 |
