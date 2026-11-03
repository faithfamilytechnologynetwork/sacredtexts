| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| terra | 100% cov 100% (n=9; c/i/r 9/0/0; minor/major 0/0) | 78% cov 100% (n=9; c/i/r 7/2/0; minor/major 2/0) | 67% cov 100% (n=9; c/i/r 6/3/0; minor/major 3/0) | 100% cov 100% (n=9; c/i/r 9/0/0; minor/major 0/0) | **86%** cov 100% (c/i/r 31/5/0; minor/major 5/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| terra | complete_unit | 2 | 2 | 0 | edition_variant 1, near_copy 1 |
| terra | retrieve_quote | 3 | 3 | 0 | edition_variant 2, near_copy 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| terra | Christianity | 100% cov 100% (n=9; c/i/r 9/0/0) | 78% cov 100% (n=9; c/i/r 7/2/0) | 67% cov 100% (n=9; c/i/r 6/3/0) | 100% cov 100% (n=9; c/i/r 9/0/0) | **86%** cov 100% (n=36; c/i/r 31/5/0) |

### By text (one text = one work · version · language)

**terra**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (the Greek New Testament (Scrivener 1894), grc) | 36 | 86% | 100% | 0 | — | 5 | 0 | edition_variant 3, near_copy 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| terra | 36 | 3,891 | 1,465 |
| **total** | 36 | 3,891 | 1,465 |
