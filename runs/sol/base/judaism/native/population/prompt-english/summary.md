| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sol | 10% cov 100% (n=30; c/i/r 3/27/0) | 27% cov 100% (n=30; c/i/r 8/22/0) | 4% cov 93% (n=30; c/i/r 1/27/2) | 77% cov 100% (n=30; c/i/r 23/7/0) | **30%** cov 98% (c/i/r 35/83/2) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sol | Judaism | 10% cov 100% (n=30; c/i/r 3/27/0) | 27% cov 100% (n=30; c/i/r 8/22/0) | 4% cov 93% (n=30; c/i/r 1/27/2) | 77% cov 100% (n=30; c/i/r 23/7/0) | **30%** cov 98% (n=120; c/i/r 35/83/2) |

### By text (one text = one work · version · language)

**sol**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 30% | 98% | 2 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sol | 120 | 11,747 | 54,070 |
| **total** | 120 | 11,747 | 54,070 |
