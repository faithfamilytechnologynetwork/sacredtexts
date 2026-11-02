| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| beam | 0% cov 77% (n=30; c/i/r 0/23/7) | 0% cov 100% (n=30; c/i/r 0/30/0) | n/a cov 0% (n=30; c/i/r 0/0/30) | 83% cov 100% (n=30; c/i/r 25/5/0) | **30%** cov 69% (c/i/r 25/58/37) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| beam | Sikhism | 0% cov 77% (n=30; c/i/r 0/23/7) | 0% cov 100% (n=30; c/i/r 0/30/0) | n/a cov 0% (n=30; c/i/r 0/0/30) | 83% cov 100% (n=30; c/i/r 25/5/0) | **30%** cov 69% (n=120; c/i/r 25/58/37) |

### By text (one text = one work · version · language)

**beam**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 120 | 30% | 69% | 37 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| beam | 120 | 20,537 | 183,548 |
| **total** | 120 | 20,537 | 183,548 |
