| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| fable | 10% cov 100% (n=30; c/i/r 3/27/0) | 7% cov 100% (n=30; c/i/r 2/28/0) | 0% cov 7% (n=30; c/i/r 0/2/28) | 90% cov 97% (n=30; c/i/r 26/3/1) | **34%** cov 76% (c/i/r 31/60/29) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| fable | Judaism | 10% cov 100% (n=30; c/i/r 3/27/0) | 7% cov 100% (n=30; c/i/r 2/28/0) | 0% cov 7% (n=30; c/i/r 0/2/28) | 90% cov 97% (n=30; c/i/r 26/3/1) | **34%** cov 76% (n=120; c/i/r 31/60/29) |

### By text (one text = one work · version · language)

**fable**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - English, en) | 120 | 34% | 76% | 29 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| fable | 120 | 17,600 | 36,383 |
| **total** | 120 | 17,600 | 36,383 |
