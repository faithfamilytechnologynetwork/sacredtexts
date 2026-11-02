| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gpt-oss-20b | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 93% (n=30; c/i/r 0/28/2) | 0% cov 70% (n=30; c/i/r 0/21/9) | 50% cov 100% (n=30; c/i/r 15/15/0) | **14%** cov 91% (c/i/r 15/94/11) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gpt-oss-20b | Judaism | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 93% (n=30; c/i/r 0/28/2) | 0% cov 70% (n=30; c/i/r 0/21/9) | 50% cov 100% (n=30; c/i/r 15/15/0) | **14%** cov 91% (n=120; c/i/r 15/94/11) |

### By text (one text = one work · version · language)

**gpt-oss-20b**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 14% | 91% | 11 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gpt-oss-20b | 120 | 18,684 | 61,822 |
| **total** | 120 | 18,684 | 61,822 |
