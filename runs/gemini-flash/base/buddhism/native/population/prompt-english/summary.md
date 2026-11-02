| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemini-flash | 90% cov 100% (n=30; c/i/r 27/3/0) | 63% cov 100% (n=30; c/i/r 19/11/0) | 47% cov 100% (n=30; c/i/r 14/16/0) | 97% cov 100% (n=30; c/i/r 29/1/0) | **74%** cov 100% (c/i/r 89/31/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemini-flash | Buddhism | 90% cov 100% (n=30; c/i/r 27/3/0) | 63% cov 100% (n=30; c/i/r 19/11/0) | 47% cov 100% (n=30; c/i/r 14/16/0) | 97% cov 100% (n=30; c/i/r 29/1/0) | **74%** cov 100% (n=120; c/i/r 89/31/0) |

### By text (one text = one work · version · language)

**gemini-flash**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Dhammapada (Chaṭṭha Saṅgāyana (VRI), pi) | 120 | 74% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemini-flash | 120 | 11,135 | 23,900 |
| **total** | 120 | 11,135 | 23,900 |
