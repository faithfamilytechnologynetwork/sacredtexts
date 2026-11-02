| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| beam | 100% cov 100% (n=30; c/i/r 30/0/0) | 80% cov 100% (n=30; c/i/r 24/6/0) | 57% cov 100% (n=30; c/i/r 17/13/0) | 93% cov 100% (n=30; c/i/r 28/2/0) | **82%** cov 100% (c/i/r 99/21/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| beam | Islam | 100% cov 100% (n=30; c/i/r 30/0/0) | 80% cov 100% (n=30; c/i/r 24/6/0) | 57% cov 100% (n=30; c/i/r 17/13/0) | 93% cov 100% (n=30; c/i/r 28/2/0) | **82%** cov 100% (n=120; c/i/r 99/21/0) |

### By text (one text = one work · version · language)

**beam**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Qur'an (Uthmani (QUL), ar) | 120 | 82% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| beam | 120 | 26,305 | 107,480 |
| **total** | 120 | 26,305 | 107,480 |
