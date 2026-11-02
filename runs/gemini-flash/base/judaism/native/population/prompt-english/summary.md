| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemini-flash | 20% cov 100% (n=30; c/i/r 6/24/0) | 13% cov 100% (n=30; c/i/r 4/26/0) | 5% cov 63% (n=30; c/i/r 1/18/11) | 50% cov 100% (n=30; c/i/r 15/15/0) | **24%** cov 91% (c/i/r 26/83/11) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemini-flash | Judaism | 20% cov 100% (n=30; c/i/r 6/24/0) | 13% cov 100% (n=30; c/i/r 4/26/0) | 5% cov 63% (n=30; c/i/r 1/18/11) | 50% cov 100% (n=30; c/i/r 15/15/0) | **24%** cov 91% (n=120; c/i/r 26/83/11) |

### By text (one text = one work · version · language)

**gemini-flash**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 24% | 91% | 11 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemini-flash | 120 | 11,433 | 255,452 |
| **total** | 120 | 11,433 | 255,452 |
