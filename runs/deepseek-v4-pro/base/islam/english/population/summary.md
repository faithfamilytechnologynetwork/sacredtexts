| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| deepseek-v4-pro | 100% cov 100% (n=30; c/i/r 30/0/0) | 23% cov 100% (n=30; c/i/r 7/23/0) | 13% cov 100% (n=30; c/i/r 4/26/0) | 83% cov 100% (n=30; c/i/r 25/5/0) | **55%** cov 100% (c/i/r 66/54/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| deepseek-v4-pro | Islam | 100% cov 100% (n=30; c/i/r 30/0/0) | 23% cov 100% (n=30; c/i/r 7/23/0) | 13% cov 100% (n=30; c/i/r 4/26/0) | 83% cov 100% (n=30; c/i/r 25/5/0) | **55%** cov 100% (n=120; c/i/r 66/54/0) |

### By text (one text = one work · version · language)

**deepseek-v4-pro**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Qur'an (Saheeh International (QUL), en) | 120 | 55% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| deepseek-v4-pro | 120 | 9,108 | 2,392 |
| **total** | 120 | 9,108 | 2,392 |
