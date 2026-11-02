| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| opus | 0% cov 100% (n=30; c/i/r 0/30/0) | 67% cov 100% (n=30; c/i/r 20/10/0) | 29% cov 23% (n=30; c/i/r 2/5/23) | 50% cov 100% (n=30; c/i/r 15/15/0) | **38%** cov 81% (c/i/r 37/60/23) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| opus | Hinduism | 0% cov 100% (n=30; c/i/r 0/30/0) | 67% cov 100% (n=30; c/i/r 20/10/0) | 29% cov 23% (n=30; c/i/r 2/5/23) | 50% cov 100% (n=30; c/i/r 15/15/0) | **38%** cov 81% (n=120; c/i/r 37/60/23) |

### By text (one text = one work · version · language)

**opus**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 38% | 81% | 23 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| opus | 120 | 16,560 | 39,597 |
| **total** | 120 | 16,560 | 39,597 |
