| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| fable | 97% cov 100% (n=30; c/i/r 29/1/0) | 67% cov 100% (n=30; c/i/r 20/10/0) | 53% cov 100% (n=30; c/i/r 16/14/0) | 52% cov 97% (n=30; c/i/r 15/14/1) | **67%** cov 99% (c/i/r 80/39/1) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| fable | Hinduism | 97% cov 100% (n=30; c/i/r 29/1/0) | 67% cov 100% (n=30; c/i/r 20/10/0) | 53% cov 100% (n=30; c/i/r 16/14/0) | 52% cov 97% (n=30; c/i/r 15/14/1) | **67%** cov 99% (n=120; c/i/r 80/39/1) |

### By text (one text = one work · version · language)

**fable**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 67% | 99% | 1 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| fable | 120 | 14,113 | 44,990 |
| **total** | 120 | 14,113 | 44,990 |
