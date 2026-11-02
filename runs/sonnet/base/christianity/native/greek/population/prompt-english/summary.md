| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sonnet | 0% cov 100% (n=9; c/i/r 0/9/0) | 78% cov 100% (n=9; c/i/r 7/2/0) | 67% cov 100% (n=9; c/i/r 6/3/0) | 100% cov 56% (n=9; c/i/r 5/0/4) | **56%** cov 89% (c/i/r 18/14/4) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sonnet | Christianity | 0% cov 100% (n=9; c/i/r 0/9/0) | 78% cov 100% (n=9; c/i/r 7/2/0) | 67% cov 100% (n=9; c/i/r 6/3/0) | 100% cov 56% (n=9; c/i/r 5/0/4) | **56%** cov 89% (n=36; c/i/r 18/14/4) |

### By text (one text = one work · version · language)

**sonnet**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Bible (the Greek New Testament (Scrivener 1894), grc) | 36 | 56% | 89% | 4 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sonnet | 36 | 5,626 | 6,161 |
| **total** | 36 | 5,626 | 6,161 |
