| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sonnet | 90% cov 100% (n=30; c/i/r 27/3/0) | 13% cov 100% (n=30; c/i/r 4/26/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 56% cov 83% (n=30; c/i/r 14/11/5) | **39%** cov 96% (c/i/r 45/70/5) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sonnet | Hinduism | 90% cov 100% (n=30; c/i/r 27/3/0) | 13% cov 100% (n=30; c/i/r 4/26/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 56% cov 83% (n=30; c/i/r 14/11/5) | **39%** cov 96% (n=120; c/i/r 45/70/5) |

### By text (one text = one work · version · language)

**sonnet**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Bhagavad Gita (Annie Besant (1922), en) | 120 | 39% | 96% | 5 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sonnet | 120 | 10,409 | 25,086 |
| **total** | 120 | 10,409 | 25,086 |
