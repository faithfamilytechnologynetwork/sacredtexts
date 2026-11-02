| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemma-31b | 53% cov 100% (n=30; c/i/r 16/14/0) | 10% cov 100% (n=30; c/i/r 3/27/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **41%** cov 100% (c/i/r 49/71/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemma-31b | Islam | 53% cov 100% (n=30; c/i/r 16/14/0) | 10% cov 100% (n=30; c/i/r 3/27/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **41%** cov 100% (n=120; c/i/r 49/71/0) |

### By text (one text = one work · version · language)

**gemma-31b**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Qur'an (Uthmani (QUL), ar) | 120 | 41% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemma-31b | 120 | 18,124 | 4,486 |
| **total** | 120 | 18,124 | 4,486 |
