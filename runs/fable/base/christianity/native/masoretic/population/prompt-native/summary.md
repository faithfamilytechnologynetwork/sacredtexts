| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| fable | 95% cov 100% (n=21; c/i/r 20/1/0) | 62% cov 100% (n=21; c/i/r 13/8/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 94% cov 76% (n=21; c/i/r 15/1/5) | **61%** cov 94% (c/i/r 48/31/5) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| fable | Christianity | 95% cov 100% (n=21; c/i/r 20/1/0) | 62% cov 100% (n=21; c/i/r 13/8/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 94% cov 76% (n=21; c/i/r 15/1/5) | **61%** cov 94% (n=84; c/i/r 48/31/5) |

### By text (one text = one work · version · language)

**fable**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 50% | 100% | 0 | — |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 61% | 94% | 5 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| fable | 84 | 14,863 | 18,236 |
| **total** | 84 | 14,863 | 18,236 |
