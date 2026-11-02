| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| opus | 100% cov 100% (n=30; c/i/r 30/0/0) | 69% cov 97% (n=30; c/i/r 20/9/1) | 55% cov 67% (n=30; c/i/r 11/9/10) | 100% cov 100% (n=30; c/i/r 30/0/0) | **83%** cov 91% (c/i/r 91/18/11) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| opus | Hinduism | 100% cov 100% (n=30; c/i/r 30/0/0) | 69% cov 97% (n=30; c/i/r 20/9/1) | 55% cov 67% (n=30; c/i/r 11/9/10) | 100% cov 100% (n=30; c/i/r 30/0/0) | **83%** cov 91% (n=120; c/i/r 91/18/11) |

### By text (one text = one work · version · language)

**opus**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Bhagavad Gita (Annie Besant (1922), en) | 120 | 83% | 91% | 11 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| opus | 120 | 10,409 | 31,792 |
| **total** | 120 | 10,409 | 31,792 |
