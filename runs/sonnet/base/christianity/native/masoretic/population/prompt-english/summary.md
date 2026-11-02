| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sonnet | 14% cov 100% (n=21; c/i/r 3/18/0) | 14% cov 100% (n=21; c/i/r 3/18/0) | 0% cov 95% (n=21; c/i/r 0/20/1) | 100% cov 48% (n=21; c/i/r 10/0/11) | **22%** cov 86% (c/i/r 16/56/12) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sonnet | Christianity | 14% cov 100% (n=21; c/i/r 3/18/0) | 14% cov 100% (n=21; c/i/r 3/18/0) | 0% cov 95% (n=21; c/i/r 0/20/1) | 100% cov 48% (n=21; c/i/r 10/0/11) | **22%** cov 86% (n=84; c/i/r 16/56/12) |

### By text (one text = one work · version · language)

**sonnet**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 25% | 100% | 0 | — |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 22% | 85% | 12 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sonnet | 84 | 17,218 | 20,102 |
| **total** | 84 | 17,218 | 20,102 |
