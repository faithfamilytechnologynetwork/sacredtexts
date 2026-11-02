| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| astra | 100% cov 100% (n=60; c/i/r 60/0/0) | 68% cov 100% (n=60; c/i/r 41/19/0) | 0% cov 100% (n=60; c/i/r 0/60/0) | 50% cov 100% (n=60; c/i/r 30/30/0) | **55%** cov 100% (c/i/r 131/109/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| astra | Hinduism | 100% cov 100% (n=60; c/i/r 60/0/0) | 68% cov 100% (n=60; c/i/r 41/19/0) | 0% cov 100% (n=60; c/i/r 0/60/0) | 50% cov 100% (n=60; c/i/r 30/30/0) | **55%** cov 100% (n=240; c/i/r 131/109/0) |

### By text (one text = one work · version · language)

**astra**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 240 | 55% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| astra | 240 | 15,948 | 21,001 |
| **total** | 240 | 15,948 | 21,001 |
