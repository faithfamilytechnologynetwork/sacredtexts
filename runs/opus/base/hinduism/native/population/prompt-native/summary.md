| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| opus | 97% cov 100% (n=30; c/i/r 29/1/0) | 70% cov 100% (n=30; c/i/r 21/9/0) | 47% cov 100% (n=30; c/i/r 14/16/0) | 52% cov 97% (n=30; c/i/r 15/14/1) | **66%** cov 99% (c/i/r 79/40/1) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| opus | Hinduism | 97% cov 100% (n=30; c/i/r 29/1/0) | 70% cov 100% (n=30; c/i/r 21/9/0) | 47% cov 100% (n=30; c/i/r 14/16/0) | 52% cov 97% (n=30; c/i/r 15/14/1) | **66%** cov 99% (n=120; c/i/r 79/40/1) |

### By text (one text = one work · version · language)

**opus**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 66% | 99% | 1 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| opus | 120 | 14,113 | 54,700 |
| **total** | 120 | 14,113 | 54,700 |
