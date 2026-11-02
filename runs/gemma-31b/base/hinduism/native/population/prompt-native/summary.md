| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemma-31b | 20% cov 100% (n=30; c/i/r 6/24/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 77% (n=30; c/i/r 0/23/7) | 97% cov 100% (n=30; c/i/r 29/1/0) | **31%** cov 94% (c/i/r 35/78/7) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemma-31b | Hinduism | 20% cov 100% (n=30; c/i/r 6/24/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 77% (n=30; c/i/r 0/23/7) | 97% cov 100% (n=30; c/i/r 29/1/0) | **31%** cov 94% (n=120; c/i/r 35/78/7) |

### By text (one text = one work · version · language)

**gemma-31b**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 31% | 94% | 7 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemma-31b | 120 | 8,232 | 5,600 |
| **total** | 120 | 8,232 | 5,600 |
