| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| astra | 33% cov 100% (n=30; c/i/r 10/20/0) | 33% cov 10% (n=30; c/i/r 1/2/27) | n/a cov 0% (n=30; c/i/r 0/0/30) | 93% cov 100% (n=30; c/i/r 28/2/0) | **62%** cov 52% (c/i/r 39/24/57) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| astra | Judaism | 33% cov 100% (n=30; c/i/r 10/20/0) | 33% cov 10% (n=30; c/i/r 1/2/27) | n/a cov 0% (n=30; c/i/r 0/0/30) | 93% cov 100% (n=30; c/i/r 28/2/0) | **62%** cov 52% (n=120; c/i/r 39/24/57) |

### By text (one text = one work · version · language)

**astra**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - English, en) | 120 | 62% | 52% | 57 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| astra | 120 | 12,190 | 26,211 |
| **total** | 120 | 12,190 | 26,211 |
