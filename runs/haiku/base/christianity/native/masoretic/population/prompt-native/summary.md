| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| haiku | 50% cov 86% (n=21; c/i/r 9/9/3) | 0% cov 95% (n=21; c/i/r 0/20/1) | 0% cov 100% (n=21; c/i/r 0/21/0) | 62% cov 76% (n=21; c/i/r 10/6/5) | **25%** cov 89% (c/i/r 19/56/9) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| haiku | Christianity | 50% cov 86% (n=21; c/i/r 9/9/3) | 0% cov 95% (n=21; c/i/r 0/20/1) | 0% cov 100% (n=21; c/i/r 0/21/0) | 62% cov 76% (n=21; c/i/r 10/6/5) | **25%** cov 89% (n=84; c/i/r 19/56/9) |

### By text (one text = one work · version · language)

**haiku**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 25% | 100% | 0 | — |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 25% | 89% | 9 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| haiku | 84 | 14,695 | 23,774 |
| **total** | 84 | 14,695 | 23,774 |
