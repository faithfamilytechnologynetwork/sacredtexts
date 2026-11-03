| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| beam | 89% cov 100% (n=9; c/i/r 8/1/0; minor/major 0/1) | 78% cov 100% (n=9; c/i/r 7/2/0; minor/major 2/0) | 56% cov 100% (n=9; c/i/r 5/4/0; minor/major 4/0) | 100% cov 100% (n=9; c/i/r 9/0/0; minor/major 0/0) | **81%** cov 100% (c/i/r 29/7/0; minor/major 6/1) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| beam | cite_passage | 1 | 0 | 1 | wrong_locus 1 |
| beam | complete_unit | 2 | 2 | 0 | edition_variant 1, near_copy 1, addition 1 |
| beam | retrieve_quote | 4 | 4 | 0 | edition_variant 2, near_copy 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| beam | Christianity | 89% cov 100% (n=9; c/i/r 8/1/0) | 78% cov 100% (n=9; c/i/r 7/2/0) | 56% cov 100% (n=9; c/i/r 5/4/0) | 100% cov 100% (n=9; c/i/r 9/0/0) | **81%** cov 100% (n=36; c/i/r 29/7/0) |

### By text (one text = one work · version · language)

**beam**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (the Greek New Testament (Scrivener 1894), grc) | 36 | 81% | 100% | 0 | — | 6 | 1 | edition_variant 3, near_copy 3, addition 1, wrong_locus 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| beam | 36 | 7,465 | 32,719 |
| **total** | 36 | 7,465 | 32,719 |
