| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| argon | 50% cov 100% (n=30; c/i/r 15/15/0) | 70% cov 100% (n=30; c/i/r 21/9/0) | 29% cov 57% (n=30; c/i/r 5/12/13) | 50% cov 100% (n=30; c/i/r 15/15/0) | **52%** cov 89% (c/i/r 56/51/13) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| argon | Hinduism | 50% cov 100% (n=30; c/i/r 15/15/0) | 70% cov 100% (n=30; c/i/r 21/9/0) | 29% cov 57% (n=30; c/i/r 5/12/13) | 50% cov 100% (n=30; c/i/r 15/15/0) | **52%** cov 89% (n=120; c/i/r 56/51/13) |

### By text (one text = one work · version · language)

**argon**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 52% | 89% | 13 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| argon | 120 | 13,546 | 3,440 |
| **total** | 120 | 13,546 | 3,440 |
