| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sonnet | 40% cov 100% (n=30; c/i/r 12/18/0) | 38% cov 97% (n=30; c/i/r 11/18/1) | 43% cov 47% (n=30; c/i/r 6/8/16) | 67% cov 30% (n=30; c/i/r 6/3/21) | **43%** cov 68% (c/i/r 35/47/38) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sonnet | Book of Mormon | 40% cov 100% (n=30; c/i/r 12/18/0) | 38% cov 97% (n=30; c/i/r 11/18/1) | 43% cov 47% (n=30; c/i/r 6/8/16) | 67% cov 30% (n=30; c/i/r 6/3/21) | **43%** cov 68% (n=120; c/i/r 35/47/38) |

### By text (one text = one work · version · language)

**sonnet**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Book of Mormon (2013 edition, en) | 120 | 43% | 68% | 38 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sonnet | 120 | 11,331 | 35,736 |
| **total** | 120 | 11,331 | 35,736 |
