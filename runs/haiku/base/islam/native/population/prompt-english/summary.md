| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| haiku | 17% cov 100% (n=30; c/i/r 5/25/0) | 70% cov 100% (n=30; c/i/r 21/9/0) | 85% cov 90% (n=30; c/i/r 23/4/3) | 100% cov 100% (n=30; c/i/r 30/0/0) | **68%** cov 98% (c/i/r 79/38/3) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| haiku | Islam | 17% cov 100% (n=30; c/i/r 5/25/0) | 70% cov 100% (n=30; c/i/r 21/9/0) | 85% cov 90% (n=30; c/i/r 23/4/3) | 100% cov 100% (n=30; c/i/r 30/0/0) | **68%** cov 98% (n=120; c/i/r 79/38/3) |

### By text (one text = one work · version · language)

**haiku**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Qur'an (Uthmani (QUL), ar) | 120 | 68% | 98% | 3 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| haiku | 120 | 27,784 | 11,603 |
| **total** | 120 | 27,784 | 11,603 |
