| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| astra | 10% cov 100% (n=30; c/i/r 3/27/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | 97% cov 100% (n=30; c/i/r 29/1/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **77%** cov 100% (c/i/r 92/28/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| astra | Islam | 10% cov 100% (n=30; c/i/r 3/27/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | 97% cov 100% (n=30; c/i/r 29/1/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **77%** cov 100% (n=120; c/i/r 92/28/0) |

### By text (one text = one work · version · language)

**astra**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Qur'an (Uthmani (QUL), ar) | 120 | 77% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| astra | 120 | 18,481 | 23,022 |
| **total** | 120 | 18,481 | 23,022 |
