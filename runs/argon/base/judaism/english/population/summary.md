| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| argon | 20% cov 100% (n=30; c/i/r 6/24/0) | 0% cov 93% (n=30; c/i/r 0/28/2) | 0% cov 10% (n=30; c/i/r 0/3/27) | 97% cov 100% (n=30; c/i/r 29/1/0) | **38%** cov 76% (c/i/r 35/56/29) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| argon | Judaism | 20% cov 100% (n=30; c/i/r 6/24/0) | 0% cov 93% (n=30; c/i/r 0/28/2) | 0% cov 10% (n=30; c/i/r 0/3/27) | 97% cov 100% (n=30; c/i/r 29/1/0) | **38%** cov 76% (n=120; c/i/r 35/56/29) |

### By text (one text = one work · version · language)

**argon**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - English, en) | 120 | 38% | 76% | 29 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| argon | 120 | 19,914 | 5,491 |
| **total** | 120 | 19,914 | 5,491 |
