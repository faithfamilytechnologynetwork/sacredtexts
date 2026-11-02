| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemini-flash | 100% cov 100% (n=30; c/i/r 30/0/0) | 50% cov 100% (n=30; c/i/r 15/15/0) | 27% cov 100% (n=30; c/i/r 8/22/0) | 97% cov 100% (n=30; c/i/r 29/1/0) | **68%** cov 100% (c/i/r 82/38/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemini-flash | Hinduism | 100% cov 100% (n=30; c/i/r 30/0/0) | 50% cov 100% (n=30; c/i/r 15/15/0) | 27% cov 100% (n=30; c/i/r 8/22/0) | 97% cov 100% (n=30; c/i/r 29/1/0) | **68%** cov 100% (n=120; c/i/r 82/38/0) |

### By text (one text = one work · version · language)

**gemini-flash**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Bhagavad Gita (Annie Besant (1922), en) | 120 | 68% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemini-flash | 120 | 6,922 | 29,426 |
| **total** | 120 | 6,922 | 29,426 |
