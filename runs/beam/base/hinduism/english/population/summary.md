| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| beam | 100% cov 100% (n=30; c/i/r 30/0/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 73% (n=30; c/i/r 0/22/8) | 97% cov 100% (n=30; c/i/r 29/1/0) | **53%** cov 93% (c/i/r 59/53/8) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| beam | Hinduism | 100% cov 100% (n=30; c/i/r 30/0/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 73% (n=30; c/i/r 0/22/8) | 97% cov 100% (n=30; c/i/r 29/1/0) | **53%** cov 93% (n=120; c/i/r 59/53/8) |

### By text (one text = one work · version · language)

**beam**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Bhagavad Gita (Annie Besant (1922), en) | 120 | 53% | 93% | 8 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| beam | 120 | 12,441 | 115,567 |
| **total** | 120 | 12,441 | 115,567 |
