| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemini-flash | 7% cov 100% (n=30; c/i/r 2/28/0) | 73% cov 100% (n=30; c/i/r 22/8/0) | 50% cov 87% (n=30; c/i/r 13/13/4) | 54% cov 93% (n=30; c/i/r 15/13/2) | **46%** cov 95% (c/i/r 52/62/6) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemini-flash | Hinduism | 7% cov 100% (n=30; c/i/r 2/28/0) | 73% cov 100% (n=30; c/i/r 22/8/0) | 50% cov 87% (n=30; c/i/r 13/13/4) | 54% cov 93% (n=30; c/i/r 15/13/2) | **46%** cov 95% (n=120; c/i/r 52/62/6) |

### By text (one text = one work · version · language)

**gemini-flash**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 46% | 95% | 6 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemini-flash | 120 | 9,555 | 40,337 |
| **total** | 120 | 9,555 | 40,337 |
