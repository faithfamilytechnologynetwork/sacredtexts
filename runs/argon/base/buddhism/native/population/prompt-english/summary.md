| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| argon | 100% cov 100% (n=2; c/i/r 2/0/0) | 50% cov 100% (n=2; c/i/r 1/1/0) | 67% cov 100% (n=3; c/i/r 2/1/0) | 100% cov 50% (n=2; c/i/r 1/0/1) | **75%** cov 89% (c/i/r 6/2/1) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| argon | Buddhism | 100% cov 100% (n=2; c/i/r 2/0/0) | 50% cov 100% (n=2; c/i/r 1/1/0) | 67% cov 100% (n=3; c/i/r 2/1/0) | 100% cov 50% (n=2; c/i/r 1/0/1) | **75%** cov 89% (n=9; c/i/r 6/2/1) |

### By text (one text = one work · version · language)

**argon**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Dhammapada (Chaṭṭha Saṅgāyana (VRI), pi) | 9 | 75% | 89% | 1 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| argon | 9 | 1,112 | 336 |
| **total** | 9 | 1,112 | 336 |
