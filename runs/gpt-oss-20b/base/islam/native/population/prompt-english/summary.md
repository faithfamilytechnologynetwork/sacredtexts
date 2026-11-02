| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gpt-oss-20b | 7% cov 97% (n=30; c/i/r 2/27/1) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 97% (n=30; c/i/r 0/29/1) | 60% cov 100% (n=30; c/i/r 18/12/0) | **17%** cov 98% (c/i/r 20/98/2) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gpt-oss-20b | Islam | 7% cov 97% (n=30; c/i/r 2/27/1) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 97% (n=30; c/i/r 0/29/1) | 60% cov 100% (n=30; c/i/r 18/12/0) | **17%** cov 98% (n=120; c/i/r 20/98/2) |

### By text (one text = one work · version · language)

**gpt-oss-20b**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Qur'an (Uthmani (QUL), ar) | 120 | 17% | 98% | 2 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gpt-oss-20b | 120 | 25,787 | 164,179 |
| **total** | 120 | 25,787 | 164,179 |
