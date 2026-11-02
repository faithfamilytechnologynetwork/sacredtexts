| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| deepseek-v4-pro | 57% cov 100% (n=30; c/i/r 17/13/0) | 23% cov 100% (n=30; c/i/r 7/23/0) | 57% cov 100% (n=30; c/i/r 17/13/0) | 30% cov 100% (n=30; c/i/r 9/21/0) | **42%** cov 100% (c/i/r 50/70/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| deepseek-v4-pro | Book of Mormon | 57% cov 100% (n=30; c/i/r 17/13/0) | 23% cov 100% (n=30; c/i/r 7/23/0) | 57% cov 100% (n=30; c/i/r 17/13/0) | 30% cov 100% (n=30; c/i/r 9/21/0) | **42%** cov 100% (n=120; c/i/r 50/70/0) |

### By text (one text = one work · version · language)

**deepseek-v4-pro**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Book of Mormon (2013 edition, en) | 120 | 42% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| deepseek-v4-pro | 120 | 7,823 | 2,008 |
| **total** | 120 | 7,823 | 2,008 |
