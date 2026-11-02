| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| fable | 100% cov 100% (n=30; c/i/r 30/0/0) | 63% cov 100% (n=30; c/i/r 19/11/0) | 43% cov 100% (n=30; c/i/r 13/17/0) | 96% cov 87% (n=30; c/i/r 25/1/4) | **75%** cov 97% (c/i/r 87/29/4) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| fable | Hinduism | 100% cov 100% (n=30; c/i/r 30/0/0) | 63% cov 100% (n=30; c/i/r 19/11/0) | 43% cov 100% (n=30; c/i/r 13/17/0) | 96% cov 87% (n=30; c/i/r 25/1/4) | **75%** cov 97% (n=120; c/i/r 87/29/4) |

### By text (one text = one work · version · language)

**fable**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Bhagavad Gita (Annie Besant (1922), en) | 120 | 75% | 97% | 4 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| fable | 120 | 10,409 | 23,164 |
| **total** | 120 | 10,409 | 23,164 |
