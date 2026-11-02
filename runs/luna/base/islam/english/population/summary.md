| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| luna | 100% cov 100% (n=30; c/i/r 30/0/0) | 27% cov 100% (n=30; c/i/r 8/22/0) | 18% cov 57% (n=30; c/i/r 3/14/13) | 93% cov 100% (n=30; c/i/r 28/2/0) | **64%** cov 89% (c/i/r 69/38/13) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| luna | Islam | 100% cov 100% (n=30; c/i/r 30/0/0) | 27% cov 100% (n=30; c/i/r 8/22/0) | 18% cov 57% (n=30; c/i/r 3/14/13) | 93% cov 100% (n=30; c/i/r 28/2/0) | **64%** cov 89% (n=120; c/i/r 69/38/13) |

### By text (one text = one work · version · language)

**luna**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Qur'an (Saheeh International (QUL), en) | 120 | 64% | 89% | 13 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| luna | 120 | 9,379 | 2,957 |
| **total** | 120 | 9,379 | 2,957 |
