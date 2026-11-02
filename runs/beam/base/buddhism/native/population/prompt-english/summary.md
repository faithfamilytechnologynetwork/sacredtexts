| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| beam | 100% cov 100% (n=2; c/i/r 2/0/0) | 0% cov 100% (n=2; c/i/r 0/2/0) | 0% cov 67% (n=3; c/i/r 0/2/1) | n/a cov 0% (n=2; c/i/r 0/0/2) | **33%** cov 67% (c/i/r 2/4/3) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| beam | Buddhism | 100% cov 100% (n=2; c/i/r 2/0/0) | 0% cov 100% (n=2; c/i/r 0/2/0) | 0% cov 67% (n=3; c/i/r 0/2/1) | n/a cov 0% (n=2; c/i/r 0/0/2) | **33%** cov 67% (n=9; c/i/r 2/4/3) |

### By text (one text = one work · version · language)

**beam**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Dhammapada (Chaṭṭha Saṅgāyana (VRI), pi) | 9 | 33% | 67% | 3 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| beam | 9 | 1,261 | 16,367 |
| **total** | 9 | 1,261 | 16,367 |
