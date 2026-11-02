| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sol | 100% cov 100% (n=30; c/i/r 30/0/0) | 60% cov 100% (n=30; c/i/r 18/12/0) | 33% cov 100% (n=30; c/i/r 10/20/0) | 97% cov 100% (n=30; c/i/r 29/1/0) | **72%** cov 100% (c/i/r 87/33/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sol | Hinduism | 100% cov 100% (n=30; c/i/r 30/0/0) | 60% cov 100% (n=30; c/i/r 18/12/0) | 33% cov 100% (n=30; c/i/r 10/20/0) | 97% cov 100% (n=30; c/i/r 29/1/0) | **72%** cov 100% (n=120; c/i/r 87/33/0) |

### By text (one text = one work · version · language)

**sol**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Bhagavad Gita (Annie Besant (1922), en) | 120 | 72% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sol | 120 | 7,363 | 18,470 |
| **total** | 120 | 7,363 | 18,470 |
