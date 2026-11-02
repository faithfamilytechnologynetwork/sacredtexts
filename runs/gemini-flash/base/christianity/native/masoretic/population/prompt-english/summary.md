| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemini-flash | 0% cov 100% (n=21; c/i/r 0/21/0) | 29% cov 100% (n=21; c/i/r 6/15/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 85% cov 95% (n=21; c/i/r 17/3/1) | **28%** cov 99% (c/i/r 23/60/1) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemini-flash | Christianity | 0% cov 100% (n=21; c/i/r 0/21/0) | 29% cov 100% (n=21; c/i/r 6/15/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 85% cov 95% (n=21; c/i/r 17/3/1) | **28%** cov 99% (n=84; c/i/r 23/60/1) |

### By text (one text = one work · version · language)

**gemini-flash**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 25% | 100% | 0 | — |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 28% | 99% | 1 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemini-flash | 84 | 10,535 | 94,533 |
| **total** | 84 | 10,535 | 94,533 |
