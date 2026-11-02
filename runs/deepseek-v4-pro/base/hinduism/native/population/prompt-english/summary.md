| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| deepseek-v4-pro | 87% cov 100% (n=30; c/i/r 26/4/0) | 23% cov 100% (n=30; c/i/r 7/23/0) | 10% cov 100% (n=30; c/i/r 3/27/0) | 58% cov 87% (n=30; c/i/r 15/11/4) | **44%** cov 97% (c/i/r 51/65/4) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| deepseek-v4-pro | Hinduism | 87% cov 100% (n=30; c/i/r 26/4/0) | 23% cov 100% (n=30; c/i/r 7/23/0) | 10% cov 100% (n=30; c/i/r 3/27/0) | 58% cov 87% (n=30; c/i/r 15/11/4) | **44%** cov 97% (n=120; c/i/r 51/65/4) |

### By text (one text = one work · version · language)

**deepseek-v4-pro**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 44% | 97% | 4 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| deepseek-v4-pro | 120 | 11,533 | 2,320 |
| **total** | 120 | 11,533 | 2,320 |
