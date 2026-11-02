| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| deepseek-v4-pro | 87% cov 100% (n=30; c/i/r 26/4/0) | 23% cov 100% (n=30; c/i/r 7/23/0) | 44% cov 60% (n=30; c/i/r 8/10/12) | 70% cov 100% (n=30; c/i/r 21/9/0) | **57%** cov 90% (c/i/r 62/46/12) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| deepseek-v4-pro | Hinduism | 87% cov 100% (n=30; c/i/r 26/4/0) | 23% cov 100% (n=30; c/i/r 7/23/0) | 44% cov 60% (n=30; c/i/r 8/10/12) | 70% cov 100% (n=30; c/i/r 21/9/0) | **57%** cov 90% (n=120; c/i/r 62/46/12) |

### By text (one text = one work · version · language)

**deepseek-v4-pro**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 57% | 90% | 12 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| deepseek-v4-pro | 120 | 10,176 | 7,587 |
| **total** | 120 | 10,176 | 7,587 |
