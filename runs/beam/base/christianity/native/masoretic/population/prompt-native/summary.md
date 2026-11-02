| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| beam | 95% cov 100% (n=21; c/i/r 20/1/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 62% cov 100% (n=21; c/i/r 13/8/0) | **39%** cov 100% (c/i/r 33/51/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| beam | Christianity | 95% cov 100% (n=21; c/i/r 20/1/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 62% cov 100% (n=21; c/i/r 13/8/0) | **39%** cov 100% (n=84; c/i/r 33/51/0) |

### By text (one text = one work · version · language)

**beam**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 50% | 100% | 0 | — |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 39% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| beam | 84 | 16,070 | 99,055 |
| **total** | 84 | 16,070 | 99,055 |
