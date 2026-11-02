| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| qwen3-32b | 57% cov 100% (n=30; c/i/r 17/13/0) | 13% cov 100% (n=30; c/i/r 4/26/0) | 7% cov 100% (n=30; c/i/r 2/28/0) | 90% cov 100% (n=30; c/i/r 27/3/0) | **42%** cov 100% (c/i/r 50/70/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| qwen3-32b | Christianity | 57% cov 100% (n=30; c/i/r 17/13/0) | 13% cov 100% (n=30; c/i/r 4/26/0) | 7% cov 100% (n=30; c/i/r 2/28/0) | 90% cov 100% (n=30; c/i/r 27/3/0) | **42%** cov 100% (n=120; c/i/r 50/70/0) |

### By text (one text = one work · version · language)

**qwen3-32b**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Bible (NRSV, en) | 120 | 42% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| qwen3-32b | 120 | 7,530 | 59,105 |
| **total** | 120 | 7,530 | 59,105 |
