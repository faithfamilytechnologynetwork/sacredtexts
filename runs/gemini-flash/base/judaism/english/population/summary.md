| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemini-flash | 7% cov 100% (n=30; c/i/r 2/28/0) | 0% cov 43% (n=30; c/i/r 0/13/17) | 0% cov 3% (n=30; c/i/r 0/1/29) | 97% cov 100% (n=30; c/i/r 29/1/0) | **42%** cov 62% (c/i/r 31/43/46) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemini-flash | Judaism | 7% cov 100% (n=30; c/i/r 2/28/0) | 0% cov 43% (n=30; c/i/r 0/13/17) | 0% cov 3% (n=30; c/i/r 0/1/29) | 97% cov 100% (n=30; c/i/r 29/1/0) | **42%** cov 62% (n=120; c/i/r 31/43/46) |

### By text (one text = one work · version · language)

**gemini-flash**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - English, en) | 120 | 42% | 62% | 46 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemini-flash | 120 | 11,338 | 33,628 |
| **total** | 120 | 11,338 | 33,628 |
