| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemini-flash | 100% cov 100% (n=21; c/i/r 21/0/0) | 19% cov 100% (n=21; c/i/r 4/17/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 86% cov 100% (n=21; c/i/r 18/3/0) | **51%** cov 100% (c/i/r 43/41/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemini-flash | Christianity | 100% cov 100% (n=21; c/i/r 21/0/0) | 19% cov 100% (n=21; c/i/r 4/17/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 86% cov 100% (n=21; c/i/r 18/3/0) | **51%** cov 100% (n=84; c/i/r 43/41/0) |

### By text (one text = one work · version · language)

**gemini-flash**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 50% | 100% | 0 | — |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 51% | 100% | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemini-flash | 84 | 9,702 | 69,856 |
| **total** | 84 | 9,702 | 69,856 |
