| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| qwen3-32b | 10% cov 100% (n=21; c/i/r 2/19/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 67% cov 86% (n=21; c/i/r 12/6/3) | **17%** cov 96% (c/i/r 14/67/3) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| qwen3-32b | Christianity | 10% cov 100% (n=21; c/i/r 2/19/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 67% cov 86% (n=21; c/i/r 12/6/3) | **17%** cov 96% (n=84; c/i/r 14/67/3) |

### By text (one text = one work · version · language)

**qwen3-32b**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 25% | 100% | 0 | — |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 17% | 96% | 3 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| qwen3-32b | 84 | 14,936 | 74,244 |
| **total** | 84 | 14,936 | 74,244 |
