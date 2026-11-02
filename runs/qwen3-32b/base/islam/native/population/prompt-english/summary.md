| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| qwen3-32b | 47% cov 100% (n=30; c/i/r 14/16/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 71% cov 70% (n=30; c/i/r 15/6/9) | **26%** cov 92% (c/i/r 29/82/9) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| qwen3-32b | Islam | 47% cov 100% (n=30; c/i/r 14/16/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 71% cov 70% (n=30; c/i/r 15/6/9) | **26%** cov 92% (n=120; c/i/r 29/82/9) |

### By text (one text = one work · version · language)

**qwen3-32b**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Qur'an (Uthmani (QUL), ar) | 120 | 26% | 92% | 9 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| qwen3-32b | 120 | 23,218 | 66,870 |
| **total** | 120 | 23,218 | 66,870 |
