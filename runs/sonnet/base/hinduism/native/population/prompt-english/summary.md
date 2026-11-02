| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sonnet | 27% cov 100% (n=30; c/i/r 8/22/0) | 70% cov 100% (n=30; c/i/r 21/9/0) | 47% cov 57% (n=30; c/i/r 8/9/13) | 26% cov 63% (n=30; c/i/r 5/14/11) | **44%** cov 80% (c/i/r 42/54/24) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sonnet | Hinduism | 27% cov 100% (n=30; c/i/r 8/22/0) | 70% cov 100% (n=30; c/i/r 21/9/0) | 47% cov 57% (n=30; c/i/r 8/9/13) | 26% cov 63% (n=30; c/i/r 5/14/11) | **44%** cov 80% (n=120; c/i/r 42/54/24) |

### By text (one text = one work · version · language)

**sonnet**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 44% | 80% | 24 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sonnet | 120 | 16,560 | 24,252 |
| **total** | 120 | 16,560 | 24,252 |
