| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| beam | 100% cov 100% (n=30; c/i/r 30/0/0) | 90% cov 100% (n=30; c/i/r 27/3/0) | 66% cov 97% (n=30; c/i/r 19/10/1) | 97% cov 100% (n=30; c/i/r 29/1/0) | **88%** cov 99% (c/i/r 105/14/1) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| beam | Islam | 100% cov 100% (n=30; c/i/r 30/0/0) | 90% cov 100% (n=30; c/i/r 27/3/0) | 66% cov 97% (n=30; c/i/r 19/10/1) | 97% cov 100% (n=30; c/i/r 29/1/0) | **88%** cov 99% (n=120; c/i/r 105/14/1) |

### By text (one text = one work · version · language)

**beam**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Qur'an (Uthmani (QUL), ar) | 120 | 88% | 99% | 1 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| beam | 120 | 27,419 | 119,653 |
| **total** | 120 | 27,419 | 119,653 |
