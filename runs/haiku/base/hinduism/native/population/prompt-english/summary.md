| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| haiku | 86% cov 93% (n=30; c/i/r 24/4/2) | 100% cov 33% (n=30; c/i/r 10/0/20) | n/a cov 0% (n=30; c/i/r 0/0/30) | 30% cov 67% (n=30; c/i/r 6/14/10) | **69%** cov 48% (c/i/r 40/18/62) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| haiku | Hinduism | 86% cov 93% (n=30; c/i/r 24/4/2) | 100% cov 33% (n=30; c/i/r 10/0/20) | n/a cov 0% (n=30; c/i/r 0/0/30) | 30% cov 67% (n=30; c/i/r 6/14/10) | **69%** cov 48% (n=120; c/i/r 40/18/62) |

### By text (one text = one work · version · language)

**haiku**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 69% | 48% | 62 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| haiku | 120 | 16,320 | 23,147 |
| **total** | 120 | 16,320 | 23,147 |
