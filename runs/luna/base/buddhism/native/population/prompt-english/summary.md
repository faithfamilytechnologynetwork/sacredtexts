| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| luna | 67% cov 100% (n=30; c/i/r 20/10/0) | 33% cov 100% (n=30; c/i/r 10/20/0) | 30% cov 100% (n=30; c/i/r 9/21/0) | 50% cov 67% (n=30; c/i/r 10/10/10) | **45%** cov 92% (c/i/r 49/61/10) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| luna | Buddhism | 67% cov 100% (n=30; c/i/r 20/10/0) | 33% cov 100% (n=30; c/i/r 10/20/0) | 30% cov 100% (n=30; c/i/r 9/21/0) | 50% cov 67% (n=30; c/i/r 10/10/10) | **45%** cov 92% (n=120; c/i/r 49/61/10) |

### By text (one text = one work · version · language)

**luna**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Dhammapada (Chaṭṭha Saṅgāyana (VRI), pi) | 120 | 45% | 92% | 10 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| luna | 120 | 11,852 | 3,206 |
| **total** | 120 | 11,852 | 3,206 |
