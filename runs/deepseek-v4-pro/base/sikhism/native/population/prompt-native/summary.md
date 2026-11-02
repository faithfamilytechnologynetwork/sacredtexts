| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| deepseek-v4-pro | 0% cov 100% (n=30; c/i/r 0/30/0) | 3% cov 100% (n=30; c/i/r 1/29/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 93% cov 100% (n=30; c/i/r 28/2/0) | **24%** cov 100% (c/i/r 29/91/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| deepseek-v4-pro | Sikhism | 0% cov 100% (n=30; c/i/r 0/30/0) | 3% cov 100% (n=30; c/i/r 1/29/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 93% cov 100% (n=30; c/i/r 28/2/0) | **24%** cov 100% (n=120; c/i/r 29/91/0) |

### By text (one text = one work · version · language)

**deepseek-v4-pro**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 120 | 24% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| deepseek-v4-pro | 120 | 14,103 | 20,918 |
| **total** | 120 | 14,103 | 20,918 |
