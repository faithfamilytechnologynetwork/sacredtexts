| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemma-31b | 73% cov 100% (n=30; c/i/r 22/8/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **43%** cov 100% (c/i/r 52/68/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemma-31b | Islam | 73% cov 100% (n=30; c/i/r 22/8/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **43%** cov 100% (n=120; c/i/r 52/68/0) |

### By text (one text = one work · version · language)

**gemma-31b**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Qur'an (Uthmani (QUL), ar) | 120 | 43% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemma-31b | 120 | 16,630 | 4,253 |
| **total** | 120 | 16,630 | 4,253 |
