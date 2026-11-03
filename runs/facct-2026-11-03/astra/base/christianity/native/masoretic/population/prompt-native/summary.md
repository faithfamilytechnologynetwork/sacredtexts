| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| astra | 100% cov 100% (n=21; c/i/r 21/0/0; minor/major 0/0) | 95% cov 100% (n=21; c/i/r 20/1/0; minor/major 1/0) | 86% cov 100% (n=21; c/i/r 18/3/0; minor/major 3/0) | 81% cov 100% (n=21; c/i/r 17/4/0; minor/major 0/4) | **90%** cov 100% (c/i/r 76/8/0; minor/major 4/4) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| astra | complete_unit | 1 | 1 | 0 | edition_variant 1 |
| astra | retrieve_quote | 3 | 3 | 0 | edition_variant 3 |
| astra | verify_source | 4 | 0 | 4 | wrong_verdict 4 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| astra | Christianity | 100% cov 100% (n=21; c/i/r 21/0/0) | 95% cov 100% (n=21; c/i/r 20/1/0) | 86% cov 100% (n=21; c/i/r 18/3/0) | 81% cov 100% (n=21; c/i/r 17/4/0) | **90%** cov 100% (n=84; c/i/r 76/8/0) |

### By text (one text = one work · version · language)

**astra**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 100% | 100% | 0 | — | 0 | 0 | — |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 90% | 100% | 0 | — | 4 | 4 | edition_variant 4, wrong_verdict 4 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| astra | 84 | 9,782 | 18,730 |
| **total** | 84 | 9,782 | 18,730 |
