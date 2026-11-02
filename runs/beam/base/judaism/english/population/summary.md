| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| beam | 3% cov 100% (n=30; c/i/r 1/29/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 7% (n=30; c/i/r 0/2/28) | 73% cov 100% (n=30; c/i/r 22/8/0) | **25%** cov 77% (c/i/r 23/69/28) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| beam | Judaism | 3% cov 100% (n=30; c/i/r 1/29/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 7% (n=30; c/i/r 0/2/28) | 73% cov 100% (n=30; c/i/r 22/8/0) | **25%** cov 77% (n=120; c/i/r 23/69/28) |

### By text (one text = one work · version · language)

**beam**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - English, en) | 120 | 25% | 77% | 28 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| beam | 120 | 17,089 | 142,821 |
| **total** | 120 | 17,089 | 142,821 |
