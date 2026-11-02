| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| qwen3-32b | 24% cov 100% (n=21; c/i/r 5/16/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 42% cov 90% (n=21; c/i/r 8/11/2) | **16%** cov 98% (c/i/r 13/69/2) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| qwen3-32b | Christianity | 24% cov 100% (n=21; c/i/r 5/16/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 42% cov 90% (n=21; c/i/r 8/11/2) | **16%** cov 98% (n=84; c/i/r 13/69/2) |

### By text (one text = one work · version · language)

**qwen3-32b**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 0% | 100% | 0 | — |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 17% | 98% | 2 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| qwen3-32b | 84 | 13,173 | 47,017 |
| **total** | 84 | 13,173 | 47,017 |
