| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gpt-oss-20b | 0% cov 100% (n=9; c/i/r 0/9/0) | 0% cov 100% (n=9; c/i/r 0/9/0) | 0% cov 89% (n=9; c/i/r 0/8/1) | 56% cov 100% (n=9; c/i/r 5/4/0) | **14%** cov 97% (c/i/r 5/30/1) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gpt-oss-20b | Christianity | 0% cov 100% (n=9; c/i/r 0/9/0) | 0% cov 100% (n=9; c/i/r 0/9/0) | 0% cov 89% (n=9; c/i/r 0/8/1) | 56% cov 100% (n=9; c/i/r 5/4/0) | **14%** cov 97% (n=36; c/i/r 5/30/1) |

### By text (one text = one work · version · language)

**gpt-oss-20b**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Bible (the Greek New Testament (Scrivener 1894), grc) | 36 | 14% | 97% | 1 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gpt-oss-20b | 36 | 6,171 | 24,796 |
| **total** | 36 | 6,171 | 24,796 |
