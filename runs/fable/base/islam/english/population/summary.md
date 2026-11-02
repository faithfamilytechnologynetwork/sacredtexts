| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| fable | 100% cov 100% (n=30; c/i/r 30/0/0) | 70% cov 100% (n=30; c/i/r 21/9/0) | 24% cov 97% (n=30; c/i/r 7/22/1) | 100% cov 100% (n=30; c/i/r 30/0/0) | **74%** cov 99% (c/i/r 88/31/1) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| fable | Islam | 100% cov 100% (n=30; c/i/r 30/0/0) | 70% cov 100% (n=30; c/i/r 21/9/0) | 24% cov 97% (n=30; c/i/r 7/22/1) | 100% cov 100% (n=30; c/i/r 30/0/0) | **74%** cov 99% (n=120; c/i/r 88/31/1) |

### By text (one text = one work · version · language)

**fable**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Qur'an (Saheeh International (QUL), en) | 120 | 74% | 99% | 1 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| fable | 120 | 13,133 | 12,616 |
| **total** | 120 | 13,133 | 12,616 |
