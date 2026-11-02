| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| qwen3-32b | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 82% cov 93% (n=30; c/i/r 23/5/2) | **19%** cov 98% (c/i/r 23/95/2) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| qwen3-32b | Judaism | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 82% cov 93% (n=30; c/i/r 23/5/2) | **19%** cov 98% (n=120; c/i/r 23/95/2) |

### By text (one text = one work · version · language)

**qwen3-32b**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 19% | 98% | 2 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| qwen3-32b | 120 | 12,802 | 102,829 |
| **total** | 120 | 12,802 | 102,829 |
