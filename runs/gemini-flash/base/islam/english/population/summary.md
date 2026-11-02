| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemini-flash | 100% cov 100% (n=30; c/i/r 30/0/0) | 25% cov 40% (n=30; c/i/r 3/9/18) | 14% cov 70% (n=30; c/i/r 3/18/9) | 100% cov 100% (n=30; c/i/r 30/0/0) | **71%** cov 78% (c/i/r 66/27/27) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemini-flash | Islam | 100% cov 100% (n=30; c/i/r 30/0/0) | 25% cov 40% (n=30; c/i/r 3/9/18) | 14% cov 70% (n=30; c/i/r 3/18/9) | 100% cov 100% (n=30; c/i/r 30/0/0) | **71%** cov 78% (n=120; c/i/r 66/27/27) |

### By text (one text = one work · version · language)

**gemini-flash**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Qur'an (Saheeh International (QUL), en) | 120 | 71% | 78% | 27 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemini-flash | 120 | 8,664 | 13,220 |
| **total** | 120 | 8,664 | 13,220 |
