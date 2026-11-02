| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| beam | 93% cov 100% (n=30; c/i/r 28/2/0) | 77% cov 100% (n=30; c/i/r 23/7/0) | 20% cov 100% (n=30; c/i/r 6/24/0) | 50% cov 100% (n=30; c/i/r 15/15/0) | **60%** cov 100% (c/i/r 72/48/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| beam | Hinduism | 93% cov 100% (n=30; c/i/r 28/2/0) | 77% cov 100% (n=30; c/i/r 23/7/0) | 20% cov 100% (n=30; c/i/r 6/24/0) | 50% cov 100% (n=30; c/i/r 15/15/0) | **60%** cov 100% (n=120; c/i/r 72/48/0) |

### By text (one text = one work · version · language)

**beam**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 60% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| beam | 120 | 19,428 | 108,155 |
| **total** | 120 | 19,428 | 108,155 |
