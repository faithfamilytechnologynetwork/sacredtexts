| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| haiku | 16% cov 83% (n=30; c/i/r 4/21/5) | 7% cov 50% (n=30; c/i/r 1/14/15) | 50% cov 7% (n=30; c/i/r 1/1/28) | 100% cov 17% (n=30; c/i/r 5/0/25) | **23%** cov 39% (c/i/r 11/36/73) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| haiku | Book of Mormon | 16% cov 83% (n=30; c/i/r 4/21/5) | 7% cov 50% (n=30; c/i/r 1/14/15) | 50% cov 7% (n=30; c/i/r 1/1/28) | 100% cov 17% (n=30; c/i/r 5/0/25) | **23%** cov 39% (n=120; c/i/r 11/36/73) |

### By text (one text = one work · version · language)

**haiku**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Book of Mormon (2013 edition, en) | 120 | 23% | 39% | 73 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| haiku | 120 | 11,091 | 15,926 |
| **total** | 120 | 11,091 | 15,926 |
