| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| argon | 100% cov 100% (n=30; c/i/r 30/0/0) | 63% cov 100% (n=30; c/i/r 19/11/0) | 44% cov 53% (n=30; c/i/r 7/9/14) | 50% cov 100% (n=30; c/i/r 15/15/0) | **67%** cov 88% (c/i/r 71/35/14) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| argon | Hinduism | 100% cov 100% (n=30; c/i/r 30/0/0) | 63% cov 100% (n=30; c/i/r 19/11/0) | 44% cov 53% (n=30; c/i/r 7/9/14) | 50% cov 100% (n=30; c/i/r 15/15/0) | **67%** cov 88% (n=120; c/i/r 71/35/14) |

### By text (one text = one work · version · language)

**argon**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 67% | 88% | 14 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| argon | 120 | 10,661 | 7,215 |
| **total** | 120 | 10,661 | 7,215 |
