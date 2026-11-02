| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| beam | 67% cov 100% (n=9; c/i/r 6/3/0) | 67% cov 100% (n=9; c/i/r 6/3/0) | 56% cov 100% (n=9; c/i/r 5/4/0) | 100% cov 100% (n=9; c/i/r 9/0/0) | **72%** cov 100% (c/i/r 26/10/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| beam | Christianity | 67% cov 100% (n=9; c/i/r 6/3/0) | 67% cov 100% (n=9; c/i/r 6/3/0) | 56% cov 100% (n=9; c/i/r 5/4/0) | 100% cov 100% (n=9; c/i/r 9/0/0) | **72%** cov 100% (n=36; c/i/r 26/10/0) |

### By text (one text = one work · version · language)

**beam**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Bible (the Greek New Testament (Scrivener 1894), grc) | 36 | 72% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| beam | 36 | 5,985 | 38,020 |
| **total** | 36 | 5,985 | 38,020 |
