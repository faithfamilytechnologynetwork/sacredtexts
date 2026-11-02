| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gpt-oss-20b | 0% cov 100% (n=21; c/i/r 0/21/0) | 0% cov 90% (n=21; c/i/r 0/19/2) | 0% cov 95% (n=21; c/i/r 0/20/1) | 81% cov 100% (n=21; c/i/r 17/4/0) | **21%** cov 96% (c/i/r 17/64/3) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gpt-oss-20b | Christianity | 0% cov 100% (n=21; c/i/r 0/21/0) | 0% cov 90% (n=21; c/i/r 0/19/2) | 0% cov 95% (n=21; c/i/r 0/20/1) | 81% cov 100% (n=21; c/i/r 17/4/0) | **21%** cov 96% (n=84; c/i/r 17/64/3) |

### By text (one text = one work · version · language)

**gpt-oss-20b**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 50% | 50% | 2 | — |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 20% | 99% | 1 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gpt-oss-20b | 84 | 15,670 | 118,594 |
| **total** | 84 | 15,670 | 118,594 |
