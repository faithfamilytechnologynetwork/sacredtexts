| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sonnet | 100% cov 100% (n=30; c/i/r 30/0/0) | 27% cov 100% (n=30; c/i/r 8/22/0) | 0% cov 80% (n=30; c/i/r 0/24/6) | 85% cov 90% (n=30; c/i/r 23/4/3) | **55%** cov 92% (c/i/r 61/50/9) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sonnet | Islam | 100% cov 100% (n=30; c/i/r 30/0/0) | 27% cov 100% (n=30; c/i/r 8/22/0) | 0% cov 80% (n=30; c/i/r 0/24/6) | 85% cov 90% (n=30; c/i/r 23/4/3) | **55%** cov 92% (n=120; c/i/r 61/50/9) |

### By text (one text = one work · version · language)

**sonnet**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Qur'an (Saheeh International (QUL), en) | 120 | 55% | 92% | 9 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sonnet | 120 | 13,133 | 15,020 |
| **total** | 120 | 13,133 | 15,020 |
