| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| fable | 0% cov 100% (n=21; c/i/r 0/21/0) | 71% cov 100% (n=21; c/i/r 15/6/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 95% cov 95% (n=21; c/i/r 19/1/1) | **41%** cov 99% (c/i/r 34/49/1) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| fable | Christianity | 0% cov 100% (n=21; c/i/r 0/21/0) | 71% cov 100% (n=21; c/i/r 15/6/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 95% cov 95% (n=21; c/i/r 19/1/1) | **41%** cov 99% (n=84; c/i/r 34/49/1) |

### By text (one text = one work · version · language)

**fable**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 25% | 100% | 0 | — |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 42% | 99% | 1 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| fable | 84 | 17,218 | 11,100 |
| **total** | 84 | 17,218 | 11,100 |
