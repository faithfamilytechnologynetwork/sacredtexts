| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| deepseek-v4-pro | 29% cov 100% (n=21; c/i/r 6/15/0) | 5% cov 100% (n=21; c/i/r 1/20/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 86% cov 100% (n=21; c/i/r 18/3/0) | **30%** cov 100% (c/i/r 25/59/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| deepseek-v4-pro | Christianity | 29% cov 100% (n=21; c/i/r 6/15/0) | 5% cov 100% (n=21; c/i/r 1/20/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 86% cov 100% (n=21; c/i/r 18/3/0) | **30%** cov 100% (n=84; c/i/r 25/59/0) |

### By text (one text = one work · version · language)

**deepseek-v4-pro**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 25% | 100% | 0 | — |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 30% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| deepseek-v4-pro | 84 | 11,556 | 3,780 |
| **total** | 84 | 11,556 | 3,780 |
