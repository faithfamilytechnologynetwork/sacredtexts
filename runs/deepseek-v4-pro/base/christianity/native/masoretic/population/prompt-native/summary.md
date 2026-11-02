| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| deepseek-v4-pro | 95% cov 100% (n=21; c/i/r 20/1/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 57% cov 100% (n=21; c/i/r 12/9/0) | **38%** cov 100% (c/i/r 32/52/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| deepseek-v4-pro | Christianity | 95% cov 100% (n=21; c/i/r 20/1/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 57% cov 100% (n=21; c/i/r 12/9/0) | **38%** cov 100% (n=84; c/i/r 32/52/0) |

### By text (one text = one work · version · language)

**deepseek-v4-pro**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 50% | 100% | 0 | — |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 38% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| deepseek-v4-pro | 84 | 10,444 | 3,996 |
| **total** | 84 | 10,444 | 3,996 |
