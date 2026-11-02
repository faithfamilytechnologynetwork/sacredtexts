| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| astra | 0% cov 100% (n=30; c/i/r 0/30/0) | 37% cov 100% (n=30; c/i/r 11/19/0) | 3% cov 100% (n=30; c/i/r 1/29/0) | 79% cov 97% (n=30; c/i/r 23/6/1) | **29%** cov 99% (c/i/r 35/84/1) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| astra | Judaism | 0% cov 100% (n=30; c/i/r 0/30/0) | 37% cov 100% (n=30; c/i/r 11/19/0) | 3% cov 100% (n=30; c/i/r 1/29/0) | 79% cov 97% (n=30; c/i/r 23/6/1) | **29%** cov 99% (n=120; c/i/r 35/84/1) |

### By text (one text = one work · version · language)

**astra**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 29% | 99% | 1 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| astra | 120 | 11,747 | 52,650 |
| **total** | 120 | 11,747 | 52,650 |
