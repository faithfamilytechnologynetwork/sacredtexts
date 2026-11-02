| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| deepseek-v4-pro | 90% cov 100% (n=30; c/i/r 27/3/0) | 67% cov 100% (n=30; c/i/r 20/10/0) | 93% cov 100% (n=30; c/i/r 28/2/0) | 97% cov 100% (n=30; c/i/r 29/1/0) | **87%** cov 100% (c/i/r 104/16/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| deepseek-v4-pro | Christianity | 90% cov 100% (n=30; c/i/r 27/3/0) | 67% cov 100% (n=30; c/i/r 20/10/0) | 93% cov 100% (n=30; c/i/r 28/2/0) | 97% cov 100% (n=30; c/i/r 29/1/0) | **87%** cov 100% (n=120; c/i/r 104/16/0) |

### By text (one text = one work · version · language)

**deepseek-v4-pro**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Bible (NRSV, en) | 120 | 87% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| deepseek-v4-pro | 120 | 6,641 | 1,816 |
| **total** | 120 | 6,641 | 1,816 |
