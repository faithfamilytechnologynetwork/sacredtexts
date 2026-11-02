| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gpt-oss-20b | 3% cov 100% (n=30; c/i/r 1/29/0) | 5% cov 73% (n=30; c/i/r 1/21/8) | 0% cov 73% (n=30; c/i/r 0/22/8) | 67% cov 100% (n=30; c/i/r 20/10/0) | **21%** cov 87% (c/i/r 22/82/16) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gpt-oss-20b | Christianity | 3% cov 100% (n=30; c/i/r 1/29/0) | 5% cov 73% (n=30; c/i/r 1/21/8) | 0% cov 73% (n=30; c/i/r 0/22/8) | 67% cov 100% (n=30; c/i/r 20/10/0) | **21%** cov 87% (n=120; c/i/r 22/82/16) |

### By text (one text = one work · version · language)

**gpt-oss-20b**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Bible (NRSV, en) | 120 | 21% | 87% | 16 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gpt-oss-20b | 120 | 14,077 | 71,170 |
| **total** | 120 | 14,077 | 71,170 |
