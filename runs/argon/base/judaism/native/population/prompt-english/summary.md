| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| argon | 10% cov 100% (n=30; c/i/r 3/27/0) | 20% cov 100% (n=30; c/i/r 6/24/0) | 0% cov 97% (n=30; c/i/r 0/29/1) | 52% cov 97% (n=30; c/i/r 15/14/1) | **20%** cov 98% (c/i/r 24/94/2) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| argon | Judaism | 10% cov 100% (n=30; c/i/r 3/27/0) | 20% cov 100% (n=30; c/i/r 6/24/0) | 0% cov 97% (n=30; c/i/r 0/29/1) | 52% cov 97% (n=30; c/i/r 15/14/1) | **20%** cov 98% (n=120; c/i/r 24/94/2) |

### By text (one text = one work · version · language)

**argon**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 20% | 98% | 2 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| argon | 120 | 17,504 | 16,651 |
| **total** | 120 | 17,504 | 16,651 |
