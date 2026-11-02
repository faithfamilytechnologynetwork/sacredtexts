| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gpt-oss-20b | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 93% (n=30; c/i/r 0/28/2) | 0% cov 10% (n=30; c/i/r 0/3/27) | 52% cov 97% (n=30; c/i/r 15/14/1) | **17%** cov 75% (c/i/r 15/75/30) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gpt-oss-20b | Judaism | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 93% (n=30; c/i/r 0/28/2) | 0% cov 10% (n=30; c/i/r 0/3/27) | 52% cov 97% (n=30; c/i/r 15/14/1) | **17%** cov 75% (n=120; c/i/r 15/75/30) |

### By text (one text = one work · version · language)

**gpt-oss-20b**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 17% | 75% | 30 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gpt-oss-20b | 120 | 19,043 | 106,411 |
| **total** | 120 | 19,043 | 106,411 |
