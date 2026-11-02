| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sol | 27% cov 100% (n=30; c/i/r 8/22/0) | 0% cov 53% (n=30; c/i/r 0/16/14) | n/a cov 0% (n=30; c/i/r 0/0/30) | 77% cov 100% (n=30; c/i/r 23/7/0) | **41%** cov 63% (c/i/r 31/45/44) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sol | Judaism | 27% cov 100% (n=30; c/i/r 8/22/0) | 0% cov 53% (n=30; c/i/r 0/16/14) | n/a cov 0% (n=30; c/i/r 0/0/30) | 77% cov 100% (n=30; c/i/r 23/7/0) | **41%** cov 63% (n=120; c/i/r 31/45/44) |

### By text (one text = one work · version · language)

**sol**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - English, en) | 120 | 41% | 63% | 44 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sol | 120 | 12,190 | 33,265 |
| **total** | 120 | 12,190 | 33,265 |
