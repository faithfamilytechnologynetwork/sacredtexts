| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| beam | 100% cov 100% (n=30; c/i/r 30/0/0) | 37% cov 100% (n=30; c/i/r 11/19/0) | 17% cov 80% (n=30; c/i/r 4/20/6) | 97% cov 100% (n=30; c/i/r 29/1/0) | **65%** cov 95% (c/i/r 74/40/6) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| beam | Islam | 100% cov 100% (n=30; c/i/r 30/0/0) | 37% cov 100% (n=30; c/i/r 11/19/0) | 17% cov 80% (n=30; c/i/r 4/20/6) | 97% cov 100% (n=30; c/i/r 29/1/0) | **65%** cov 95% (n=120; c/i/r 74/40/6) |

### By text (one text = one work · version · language)

**beam**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Qur'an (Saheeh International (QUL), en) | 120 | 65% | 95% | 6 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| beam | 120 | 14,225 | 69,828 |
| **total** | 120 | 14,225 | 69,828 |
