| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sol | 7% cov 100% (n=30; c/i/r 2/28/0) | 70% cov 100% (n=30; c/i/r 21/9/0) | 4% cov 87% (n=30; c/i/r 1/25/4) | 52% cov 97% (n=30; c/i/r 15/14/1) | **34%** cov 96% (c/i/r 39/76/5) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sol | Hinduism | 7% cov 100% (n=30; c/i/r 2/28/0) | 70% cov 100% (n=30; c/i/r 21/9/0) | 4% cov 87% (n=30; c/i/r 1/25/4) | 52% cov 97% (n=30; c/i/r 15/14/1) | **34%** cov 96% (n=120; c/i/r 39/76/5) |

### By text (one text = one work · version · language)

**sol**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 34% | 96% | 5 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sol | 120 | 10,766 | 15,443 |
| **total** | 120 | 10,766 | 15,443 |
