| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemini-flash | 100% cov 100% (n=30; c/i/r 30/0/0) | 70% cov 100% (n=30; c/i/r 21/9/0) | 40% cov 100% (n=30; c/i/r 12/18/0) | 73% cov 100% (n=30; c/i/r 22/8/0) | **71%** cov 100% (c/i/r 85/35/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemini-flash | Hinduism | 100% cov 100% (n=30; c/i/r 30/0/0) | 70% cov 100% (n=30; c/i/r 21/9/0) | 40% cov 100% (n=30; c/i/r 12/18/0) | 73% cov 100% (n=30; c/i/r 22/8/0) | **71%** cov 100% (n=120; c/i/r 85/35/0) |

### By text (one text = one work · version · language)

**gemini-flash**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 71% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemini-flash | 120 | 6,684 | 12,947 |
| **total** | 120 | 6,684 | 12,947 |
