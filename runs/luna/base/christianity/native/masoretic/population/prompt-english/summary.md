| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| luna | 90% cov 100% (n=21; c/i/r 19/2/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 62% cov 100% (n=21; c/i/r 13/8/0) | **38%** cov 100% (c/i/r 32/52/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| luna | Christianity | 90% cov 100% (n=21; c/i/r 19/2/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 62% cov 100% (n=21; c/i/r 13/8/0) | **38%** cov 100% (n=84; c/i/r 32/52/0) |

### By text (one text = one work · version · language)

**luna**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 50% | 100% | 0 | — |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 38% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| luna | 84 | 12,357 | 4,860 |
| **total** | 84 | 12,357 | 4,860 |
