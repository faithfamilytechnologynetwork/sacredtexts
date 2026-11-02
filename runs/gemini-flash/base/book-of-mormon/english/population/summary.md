| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemini-flash | 87% cov 100% (n=30; c/i/r 26/4/0) | 62% cov 97% (n=30; c/i/r 18/11/1) | 50% cov 93% (n=30; c/i/r 14/14/2) | 80% cov 100% (n=30; c/i/r 24/6/0) | **70%** cov 98% (c/i/r 82/35/3) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemini-flash | Book of Mormon | 87% cov 100% (n=30; c/i/r 26/4/0) | 62% cov 97% (n=30; c/i/r 18/11/1) | 50% cov 93% (n=30; c/i/r 14/14/2) | 80% cov 100% (n=30; c/i/r 24/6/0) | **70%** cov 98% (n=120; c/i/r 82/35/3) |

### By text (one text = one work · version · language)

**gemini-flash**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Book of Mormon (2013 edition, en) | 120 | 70% | 98% | 3 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemini-flash | 120 | 7,601 | 28,680 |
| **total** | 120 | 7,601 | 28,680 |
