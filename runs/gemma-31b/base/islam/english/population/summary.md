| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemma-31b | 50% cov 100% (n=30; c/i/r 15/15/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 83% cov 100% (n=30; c/i/r 25/5/0) | **33%** cov 100% (c/i/r 40/80/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemma-31b | Islam | 50% cov 100% (n=30; c/i/r 15/15/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 83% cov 100% (n=30; c/i/r 25/5/0) | **33%** cov 100% (n=120; c/i/r 40/80/0) |

### By text (one text = one work · version · language)

**gemma-31b**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Qur'an (Saheeh International (QUL), en) | 120 | 33% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemma-31b | 120 | 10,246 | 1,902 |
| **total** | 120 | 10,246 | 1,902 |
