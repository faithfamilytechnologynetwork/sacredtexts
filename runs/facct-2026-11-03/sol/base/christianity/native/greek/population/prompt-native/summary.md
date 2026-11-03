| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sol | 100% cov 100% (n=9; c/i/r 9/0/0; minor/major 0/0) | 89% cov 100% (n=9; c/i/r 8/1/0; minor/major 1/0) | 78% cov 100% (n=9; c/i/r 7/2/0; minor/major 2/0) | 100% cov 100% (n=9; c/i/r 9/0/0; minor/major 0/0) | **92%** cov 100% (c/i/r 33/3/0; minor/major 3/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sol | complete_unit | 1 | 1 | 0 | edition_variant 1 |
| sol | retrieve_quote | 2 | 2 | 0 | edition_variant 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sol | Christianity | 100% cov 100% (n=9; c/i/r 9/0/0) | 89% cov 100% (n=9; c/i/r 8/1/0) | 78% cov 100% (n=9; c/i/r 7/2/0) | 100% cov 100% (n=9; c/i/r 9/0/0) | **92%** cov 100% (n=36; c/i/r 33/3/0) |

### By text (one text = one work · version · language)

**sol**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (the Greek New Testament (Scrivener 1894), grc) | 36 | 92% | 100% | 0 | — | 3 | 0 | edition_variant 3 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sol | 36 | 3,840 | 4,966 |
| **total** | 36 | 3,840 | 4,966 |
