| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sol | 100% cov 100% (n=30; c/i/r 30/0/0) | 70% cov 100% (n=30; c/i/r 21/9/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 53% cov 100% (n=30; c/i/r 16/14/0) | **56%** cov 100% (c/i/r 67/53/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sol | Hinduism | 100% cov 100% (n=30; c/i/r 30/0/0) | 70% cov 100% (n=30; c/i/r 21/9/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 53% cov 100% (n=30; c/i/r 16/14/0) | **56%** cov 100% (n=120; c/i/r 67/53/0) |

### By text (one text = one work · version · language)

**sol**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 56% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sol | 120 | 7,974 | 11,929 |
| **total** | 120 | 7,974 | 11,929 |
