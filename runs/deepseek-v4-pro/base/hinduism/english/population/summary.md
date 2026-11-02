| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| deepseek-v4-pro | 67% cov 100% (n=30; c/i/r 20/10/0) | 3% cov 100% (n=30; c/i/r 1/29/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 67% cov 100% (n=30; c/i/r 20/10/0) | **34%** cov 100% (c/i/r 41/79/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| deepseek-v4-pro | Hinduism | 67% cov 100% (n=30; c/i/r 20/10/0) | 3% cov 100% (n=30; c/i/r 1/29/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 67% cov 100% (n=30; c/i/r 20/10/0) | **34%** cov 100% (n=120; c/i/r 41/79/0) |

### By text (one text = one work · version · language)

**deepseek-v4-pro**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Bhagavad Gita (Annie Besant (1922), en) | 120 | 34% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| deepseek-v4-pro | 120 | 7,129 | 1,663 |
| **total** | 120 | 7,129 | 1,663 |
