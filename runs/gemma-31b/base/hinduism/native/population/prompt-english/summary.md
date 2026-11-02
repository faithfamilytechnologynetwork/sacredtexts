| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemma-31b | 13% cov 100% (n=30; c/i/r 4/26/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 50% (n=30; c/i/r 0/15/15) | 100% cov 40% (n=30; c/i/r 12/0/18) | **18%** cov 72% (c/i/r 16/71/33) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemma-31b | Hinduism | 13% cov 100% (n=30; c/i/r 4/26/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 50% (n=30; c/i/r 0/15/15) | 100% cov 40% (n=30; c/i/r 12/0/18) | **18%** cov 72% (n=120; c/i/r 16/71/33) |

### By text (one text = one work · version · language)

**gemma-31b**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 18% | 72% | 33 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemma-31b | 120 | 11,111 | 6,610 |
| **total** | 120 | 11,111 | 6,610 |
