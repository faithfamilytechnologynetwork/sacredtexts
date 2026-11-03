| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| fable | 100% cov 100% (n=9; c/i/r 9/0/0; minor/major 0/0) | 100% cov 100% (n=9; c/i/r 9/0/0; minor/major 0/0) | 100% cov 100% (n=9; c/i/r 9/0/0; minor/major 0/0) | 100% cov 89% (n=9; c/i/r 8/0/1; minor/major 0/0) | **100%** cov 97% (c/i/r 35/0/1; minor/major 0/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| fable | Christianity | 100% cov 100% (n=9; c/i/r 9/0/0) | 100% cov 100% (n=9; c/i/r 9/0/0) | 100% cov 100% (n=9; c/i/r 9/0/0) | 100% cov 89% (n=9; c/i/r 8/0/1) | **100%** cov 97% (n=36; c/i/r 35/0/1) |

### By text (one text = one work · version · language)

**fable**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (the Greek New Testament (Scrivener 1894), grc) | 36 | 100% | 97% | 1 | — | 0 | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| fable | 36 | 5,784 | 3,280 |
| **total** | 36 | 5,784 | 3,280 |
