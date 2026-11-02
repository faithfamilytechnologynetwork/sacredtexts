| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| haiku | 40% cov 100% (n=30; c/i/r 12/18/0) | 53% cov 100% (n=30; c/i/r 16/14/0) | 10% cov 100% (n=30; c/i/r 3/27/0) | 100% cov 50% (n=30; c/i/r 15/0/15) | **44%** cov 88% (c/i/r 46/59/15) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| haiku | Hinduism | 40% cov 100% (n=30; c/i/r 12/18/0) | 53% cov 100% (n=30; c/i/r 16/14/0) | 10% cov 100% (n=30; c/i/r 3/27/0) | 100% cov 50% (n=30; c/i/r 15/0/15) | **44%** cov 88% (n=120; c/i/r 46/59/15) |

### By text (one text = one work · version · language)

**haiku**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 44% | 88% | 15 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| haiku | 120 | 13,873 | 50,204 |
| **total** | 120 | 13,873 | 50,204 |
