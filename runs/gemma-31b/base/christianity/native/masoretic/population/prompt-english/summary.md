| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemma-31b | 5% cov 100% (n=21; c/i/r 1/20/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 86% cov 100% (n=21; c/i/r 18/3/0) | **23%** cov 100% (c/i/r 19/65/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemma-31b | Christianity | 5% cov 100% (n=21; c/i/r 1/20/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 86% cov 100% (n=21; c/i/r 18/3/0) | **23%** cov 100% (n=84; c/i/r 19/65/0) |

### By text (one text = one work · version · language)

**gemma-31b**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 25% | 100% | 0 | — |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 22% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemma-31b | 84 | 11,622 | 2,933 |
| **total** | 84 | 11,622 | 2,933 |
