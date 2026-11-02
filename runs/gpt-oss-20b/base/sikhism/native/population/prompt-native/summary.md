| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gpt-oss-20b | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 53% (n=30; c/i/r 0/16/14) | 50% cov 100% (n=30; c/i/r 15/15/0) | **14%** cov 88% (c/i/r 15/91/14) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gpt-oss-20b | Sikhism | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 53% (n=30; c/i/r 0/16/14) | 50% cov 100% (n=30; c/i/r 15/15/0) | **14%** cov 88% (n=120; c/i/r 15/91/14) |

### By text (one text = one work · version · language)

**gpt-oss-20b**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 120 | 14% | 88% | 14 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gpt-oss-20b | 120 | 17,207 | 154,139 |
| **total** | 120 | 17,207 | 154,139 |
