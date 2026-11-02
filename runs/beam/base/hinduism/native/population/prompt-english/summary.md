| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| beam | 100% cov 100% (n=30; c/i/r 30/0/0) | 73% cov 100% (n=30; c/i/r 22/8/0) | 0% cov 3% (n=30; c/i/r 0/1/29) | 50% cov 100% (n=30; c/i/r 15/15/0) | **74%** cov 76% (c/i/r 67/24/29) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| beam | Hinduism | 100% cov 100% (n=30; c/i/r 30/0/0) | 73% cov 100% (n=30; c/i/r 22/8/0) | 0% cov 3% (n=30; c/i/r 0/1/29) | 50% cov 100% (n=30; c/i/r 15/15/0) | **74%** cov 76% (n=120; c/i/r 67/24/29) |

### By text (one text = one work · version · language)

**beam**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 74% | 76% | 29 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| beam | 120 | 18,952 | 113,607 |
| **total** | 120 | 18,952 | 113,607 |
