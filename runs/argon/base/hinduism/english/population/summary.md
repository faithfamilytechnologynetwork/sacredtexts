| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| argon | 100% cov 100% (n=30; c/i/r 30/0/0) | 41% cov 97% (n=30; c/i/r 12/17/1) | 11% cov 90% (n=30; c/i/r 3/24/3) | 100% cov 100% (n=30; c/i/r 30/0/0) | **65%** cov 97% (c/i/r 75/41/4) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| argon | Hinduism | 100% cov 100% (n=30; c/i/r 30/0/0) | 41% cov 97% (n=30; c/i/r 12/17/1) | 11% cov 90% (n=30; c/i/r 3/24/3) | 100% cov 100% (n=30; c/i/r 30/0/0) | **65%** cov 97% (n=120; c/i/r 75/41/4) |

### By text (one text = one work · version · language)

**argon**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Bhagavad Gita (Annie Besant (1922), en) | 120 | 65% | 97% | 4 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| argon | 120 | 12,014 | 2,487 |
| **total** | 120 | 12,014 | 2,487 |
