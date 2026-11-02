| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| luna | 7% cov 100% (n=30; c/i/r 2/28/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 63% (n=30; c/i/r 0/19/11) | 53% cov 100% (n=30; c/i/r 16/14/0) | **17%** cov 91% (c/i/r 18/91/11) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| luna | Judaism | 7% cov 100% (n=30; c/i/r 2/28/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 63% (n=30; c/i/r 0/19/11) | 53% cov 100% (n=30; c/i/r 16/14/0) | **17%** cov 91% (n=120; c/i/r 18/91/11) |

### By text (one text = one work · version · language)

**luna**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - English, en) | 120 | 17% | 91% | 11 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| luna | 120 | 12,190 | 10,344 |
| **total** | 120 | 12,190 | 10,344 |
