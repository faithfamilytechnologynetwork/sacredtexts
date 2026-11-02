| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemini-flash | 3% cov 100% (n=30; c/i/r 1/29/0) | 97% cov 100% (n=30; c/i/r 29/1/0) | 93% cov 100% (n=30; c/i/r 28/2/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **73%** cov 100% (c/i/r 88/32/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemini-flash | Islam | 3% cov 100% (n=30; c/i/r 1/29/0) | 97% cov 100% (n=30; c/i/r 29/1/0) | 93% cov 100% (n=30; c/i/r 28/2/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **73%** cov 100% (n=120; c/i/r 88/32/0) |

### By text (one text = one work · version · language)

**gemini-flash**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Qur'an (Uthmani (QUL), ar) | 120 | 73% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemini-flash | 120 | 16,530 | 17,341 |
| **total** | 120 | 16,530 | 17,341 |
