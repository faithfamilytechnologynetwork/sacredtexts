| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| luna | 93% cov 100% (n=30; c/i/r 28/2/0) | 0% cov 97% (n=30; c/i/r 0/29/1) | 0% cov 73% (n=30; c/i/r 0/22/8) | 83% cov 100% (n=30; c/i/r 25/5/0) | **48%** cov 92% (c/i/r 53/58/9) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| luna | Hinduism | 93% cov 100% (n=30; c/i/r 28/2/0) | 0% cov 97% (n=30; c/i/r 0/29/1) | 0% cov 73% (n=30; c/i/r 0/22/8) | 83% cov 100% (n=30; c/i/r 25/5/0) | **48%** cov 92% (n=120; c/i/r 53/58/9) |

### By text (one text = one work · version · language)

**luna**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Bhagavad Gita (Annie Besant (1922), en) | 120 | 48% | 92% | 9 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| luna | 120 | 7,363 | 1,648 |
| **total** | 120 | 7,363 | 1,648 |
