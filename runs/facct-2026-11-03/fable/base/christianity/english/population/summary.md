| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| fable | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | 90% cov 100% (n=30; c/i/r 27/3/0; minor/major 3/0) | 100% cov 97% (n=30; c/i/r 29/0/1; minor/major 0/0) | 100% cov 97% (n=30; c/i/r 29/0/1; minor/major 0/0) | **97%** cov 98% (c/i/r 114/4/2; minor/major 3/1) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| fable | cite_passage | 1 | 0 | 1 | hedge 1 |
| fable | complete_unit | 3 | 3 | 0 | edition_variant 2, near_copy 1, addition 4 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| fable | Christianity | 97% cov 100% (n=30; c/i/r 29/1/0) | 90% cov 100% (n=30; c/i/r 27/3/0) | 100% cov 97% (n=30; c/i/r 29/0/1) | 100% cov 97% (n=30; c/i/r 29/0/1) | **97%** cov 98% (n=120; c/i/r 114/4/2) |

### By text (one text = one work · version · language)

**fable**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (NRSV, en) | 120 | 97% | 98% | 2 | — | 3 | 1 | edition_variant 2, near_copy 1, addition 4, hedge 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| fable | 120 | 9,947 | 5,634 |
| **total** | 120 | 9,947 | 5,634 |
