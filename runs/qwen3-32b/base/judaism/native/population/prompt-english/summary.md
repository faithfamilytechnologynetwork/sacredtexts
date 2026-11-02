| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| qwen3-32b | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 97% (n=30; c/i/r 0/29/1) | 55% cov 97% (n=30; c/i/r 16/13/1) | **14%** cov 98% (c/i/r 16/102/2) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| qwen3-32b | Judaism | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 97% (n=30; c/i/r 0/29/1) | 55% cov 97% (n=30; c/i/r 16/13/1) | **14%** cov 98% (n=120; c/i/r 16/102/2) |

### By text (one text = one work · version · language)

**qwen3-32b**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 14% | 98% | 2 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| qwen3-32b | 120 | 13,340 | 80,701 |
| **total** | 120 | 13,340 | 80,701 |
