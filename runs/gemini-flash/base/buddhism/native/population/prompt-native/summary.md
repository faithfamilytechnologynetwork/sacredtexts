| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemini-flash | 90% cov 100% (n=30; c/i/r 27/3/0) | 57% cov 100% (n=30; c/i/r 17/13/0) | 43% cov 100% (n=30; c/i/r 13/17/0) | 90% cov 100% (n=30; c/i/r 27/3/0) | **70%** cov 100% (c/i/r 84/36/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemini-flash | Buddhism | 90% cov 100% (n=30; c/i/r 27/3/0) | 57% cov 100% (n=30; c/i/r 17/13/0) | 43% cov 100% (n=30; c/i/r 13/17/0) | 90% cov 100% (n=30; c/i/r 27/3/0) | **70%** cov 100% (n=120; c/i/r 84/36/0) |

### By text (one text = one work · version · language)

**gemini-flash**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Dhammapada (Chaṭṭha Saṅgāyana (VRI), pi) | 120 | 70% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemini-flash | 120 | 9,654 | 17,290 |
| **total** | 120 | 9,654 | 17,290 |
