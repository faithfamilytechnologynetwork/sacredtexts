| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| terra | 95% cov 100% (n=21; c/i/r 20/1/0) | 29% cov 100% (n=21; c/i/r 6/15/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 71% cov 100% (n=21; c/i/r 15/6/0) | **49%** cov 100% (c/i/r 41/43/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| terra | Christianity | 95% cov 100% (n=21; c/i/r 20/1/0) | 29% cov 100% (n=21; c/i/r 6/15/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 71% cov 100% (n=21; c/i/r 15/6/0) | **49%** cov 100% (n=84; c/i/r 41/43/0) |

### By text (one text = one work · version · language)

**terra**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 50% | 100% | 0 | — |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 49% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| terra | 84 | 10,574 | 4,997 |
| **total** | 84 | 10,574 | 4,997 |
