| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gpt-oss-20b | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 80% (n=30; c/i/r 0/24/6) | n/a cov 0% (n=30; c/i/r 0/0/30) | 50% cov 100% (n=30; c/i/r 15/15/0) | **18%** cov 70% (c/i/r 15/69/36) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gpt-oss-20b | Hinduism | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 80% (n=30; c/i/r 0/24/6) | n/a cov 0% (n=30; c/i/r 0/0/30) | 50% cov 100% (n=30; c/i/r 15/15/0) | **18%** cov 70% (n=120; c/i/r 15/69/36) |

### By text (one text = one work · version · language)

**gpt-oss-20b**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 18% | 70% | 36 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gpt-oss-20b | 120 | 15,280 | 18,449 |
| **total** | 120 | 15,280 | 18,449 |
