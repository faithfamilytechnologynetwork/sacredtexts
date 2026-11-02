| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemini-flash | 17% cov 100% (n=30; c/i/r 5/25/0) | 7% cov 100% (n=30; c/i/r 2/28/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 87% cov 100% (n=30; c/i/r 26/4/0) | **28%** cov 100% (c/i/r 33/87/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemini-flash | Judaism | 17% cov 100% (n=30; c/i/r 5/25/0) | 7% cov 100% (n=30; c/i/r 2/28/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 87% cov 100% (n=30; c/i/r 26/4/0) | **28%** cov 100% (n=120; c/i/r 33/87/0) |

### By text (one text = one work · version · language)

**gemini-flash**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 28% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemini-flash | 120 | 11,565 | 71,923 |
| **total** | 120 | 11,565 | 71,923 |
