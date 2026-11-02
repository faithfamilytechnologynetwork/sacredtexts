| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemini-flash | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 93% (n=30; c/i/r 0/28/2) | 60% cov 100% (n=30; c/i/r 18/12/0) | **15%** cov 98% (c/i/r 18/100/2) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemini-flash | Sikhism | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 93% (n=30; c/i/r 0/28/2) | 60% cov 100% (n=30; c/i/r 18/12/0) | **15%** cov 98% (n=120; c/i/r 18/100/2) |

### By text (one text = one work · version · language)

**gemini-flash**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 120 | 15% | 98% | 2 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemini-flash | 120 | 10,661 | 85,941 |
| **total** | 120 | 10,661 | 85,941 |
