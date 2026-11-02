| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| terra | 10% cov 100% (n=30; c/i/r 3/27/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 97% (n=30; c/i/r 0/29/1) | 83% cov 100% (n=30; c/i/r 25/5/0) | **24%** cov 99% (c/i/r 28/91/1) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| terra | Judaism | 10% cov 100% (n=30; c/i/r 3/27/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 97% (n=30; c/i/r 0/29/1) | 83% cov 100% (n=30; c/i/r 25/5/0) | **24%** cov 99% (n=120; c/i/r 28/91/1) |

### By text (one text = one work · version · language)

**terra**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - English, en) | 120 | 24% | 99% | 1 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| terra | 120 | 12,190 | 5,374 |
| **total** | 120 | 12,190 | 5,374 |
