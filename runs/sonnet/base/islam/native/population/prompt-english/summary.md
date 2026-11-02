| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sonnet | 3% cov 100% (n=30; c/i/r 1/29/0) | 97% cov 100% (n=30; c/i/r 29/1/0) | 97% cov 100% (n=30; c/i/r 29/1/0) | 100% cov 73% (n=30; c/i/r 22/0/8) | **72%** cov 93% (c/i/r 81/31/8) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sonnet | Islam | 3% cov 100% (n=30; c/i/r 1/29/0) | 97% cov 100% (n=30; c/i/r 29/1/0) | 97% cov 100% (n=30; c/i/r 29/1/0) | 100% cov 73% (n=30; c/i/r 22/0/8) | **72%** cov 93% (n=120; c/i/r 81/31/8) |

### By text (one text = one work · version · language)

**sonnet**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Qur'an (Uthmani (QUL), ar) | 120 | 72% | 93% | 8 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sonnet | 120 | 28,024 | 23,337 |
| **total** | 120 | 28,024 | 23,337 |
