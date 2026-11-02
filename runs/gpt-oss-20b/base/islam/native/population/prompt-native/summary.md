| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gpt-oss-20b | 3% cov 100% (n=30; c/i/r 1/29/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 53% cov 100% (n=30; c/i/r 16/14/0) | **14%** cov 100% (c/i/r 17/103/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gpt-oss-20b | Islam | 3% cov 100% (n=30; c/i/r 1/29/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 53% cov 100% (n=30; c/i/r 16/14/0) | **14%** cov 100% (n=120; c/i/r 17/103/0) |

### By text (one text = one work · version · language)

**gpt-oss-20b**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Qur'an (Uthmani (QUL), ar) | 120 | 14% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gpt-oss-20b | 120 | 24,412 | 105,759 |
| **total** | 120 | 24,412 | 105,759 |
