| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| deepseek-v4-pro | 70% cov 100% (n=30; c/i/r 21/9/0) | 53% cov 100% (n=30; c/i/r 16/14/0) | 77% cov 100% (n=30; c/i/r 23/7/0) | 97% cov 100% (n=30; c/i/r 29/1/0) | **74%** cov 100% (c/i/r 89/31/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| deepseek-v4-pro | Islam | 70% cov 100% (n=30; c/i/r 21/9/0) | 53% cov 100% (n=30; c/i/r 16/14/0) | 77% cov 100% (n=30; c/i/r 23/7/0) | 97% cov 100% (n=30; c/i/r 29/1/0) | **74%** cov 100% (n=120; c/i/r 89/31/0) |

### By text (one text = one work · version · language)

**deepseek-v4-pro**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Qur'an (Uthmani (QUL), ar) | 120 | 74% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| deepseek-v4-pro | 120 | 17,910 | 6,943 |
| **total** | 120 | 17,910 | 6,943 |
