| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| terra | 10% cov 100% (n=30; c/i/r 3/27/0) | 60% cov 100% (n=30; c/i/r 18/12/0) | 29% cov 93% (n=30; c/i/r 8/20/2) | 67% cov 100% (n=30; c/i/r 20/10/0) | **42%** cov 98% (c/i/r 49/69/2) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| terra | Hinduism | 10% cov 100% (n=30; c/i/r 3/27/0) | 60% cov 100% (n=30; c/i/r 18/12/0) | 29% cov 93% (n=30; c/i/r 8/20/2) | 67% cov 100% (n=30; c/i/r 20/10/0) | **42%** cov 98% (n=120; c/i/r 49/69/2) |

### By text (one text = one work · version · language)

**terra**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 42% | 98% | 2 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| terra | 120 | 10,766 | 2,587 |
| **total** | 120 | 10,766 | 2,587 |
