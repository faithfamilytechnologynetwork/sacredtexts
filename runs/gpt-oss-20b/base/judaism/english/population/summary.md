| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gpt-oss-20b | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 93% (n=30; c/i/r 0/28/2) | n/a cov 0% (n=30; c/i/r 0/0/30) | 50% cov 100% (n=30; c/i/r 15/15/0) | **17%** cov 73% (c/i/r 15/73/32) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gpt-oss-20b | Judaism | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 93% (n=30; c/i/r 0/28/2) | n/a cov 0% (n=30; c/i/r 0/0/30) | 50% cov 100% (n=30; c/i/r 15/15/0) | **17%** cov 73% (n=120; c/i/r 15/73/32) |

### By text (one text = one work · version · language)

**gpt-oss-20b**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - English, en) | 120 | 17% | 73% | 32 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gpt-oss-20b | 120 | 19,512 | 66,792 |
| **total** | 120 | 19,512 | 66,792 |
