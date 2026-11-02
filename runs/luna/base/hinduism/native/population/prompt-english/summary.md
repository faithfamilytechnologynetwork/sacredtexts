| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| luna | 100% cov 100% (n=30; c/i/r 30/0/0) | 40% cov 100% (n=30; c/i/r 12/18/0) | 4% cov 87% (n=30; c/i/r 1/25/4) | 79% cov 80% (n=30; c/i/r 19/5/6) | **56%** cov 92% (c/i/r 62/48/10) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| luna | Hinduism | 100% cov 100% (n=30; c/i/r 30/0/0) | 40% cov 100% (n=30; c/i/r 12/18/0) | 4% cov 87% (n=30; c/i/r 1/25/4) | 79% cov 80% (n=30; c/i/r 19/5/6) | **56%** cov 92% (n=120; c/i/r 62/48/10) |

### By text (one text = one work · version · language)

**luna**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 56% | 92% | 10 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| luna | 120 | 10,766 | 2,195 |
| **total** | 120 | 10,766 | 2,195 |
