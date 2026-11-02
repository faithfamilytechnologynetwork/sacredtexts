| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| fable | 0% cov 100% (n=30; c/i/r 0/30/0) | 23% cov 100% (n=30; c/i/r 7/23/0) | 3% cov 100% (n=30; c/i/r 1/29/0) | 100% cov 83% (n=30; c/i/r 25/0/5) | **29%** cov 96% (c/i/r 33/82/5) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| fable | Judaism | 0% cov 100% (n=30; c/i/r 0/30/0) | 23% cov 100% (n=30; c/i/r 7/23/0) | 3% cov 100% (n=30; c/i/r 1/29/0) | 100% cov 83% (n=30; c/i/r 25/0/5) | **29%** cov 96% (n=120; c/i/r 33/82/5) |

### By text (one text = one work · version · language)

**fable**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 29% | 96% | 5 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| fable | 120 | 17,859 | 88,035 |
| **total** | 120 | 17,859 | 88,035 |
