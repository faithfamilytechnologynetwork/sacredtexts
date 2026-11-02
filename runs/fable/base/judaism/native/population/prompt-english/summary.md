| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| fable | 0% cov 100% (n=30; c/i/r 0/30/0) | 17% cov 100% (n=30; c/i/r 5/25/0) | 3% cov 100% (n=30; c/i/r 1/29/0) | 56% cov 90% (n=30; c/i/r 15/12/3) | **18%** cov 98% (c/i/r 21/96/3) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| fable | Judaism | 0% cov 100% (n=30; c/i/r 0/30/0) | 17% cov 100% (n=30; c/i/r 5/25/0) | 3% cov 100% (n=30; c/i/r 1/29/0) | 56% cov 90% (n=30; c/i/r 15/12/3) | **18%** cov 98% (n=120; c/i/r 21/96/3) |

### By text (one text = one work · version · language)

**fable**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 18% | 98% | 3 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| fable | 120 | 18,252 | 72,120 |
| **total** | 120 | 18,252 | 72,120 |
