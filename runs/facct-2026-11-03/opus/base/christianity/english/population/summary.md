| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| opus | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 90% cov 100% (n=30; c/i/r 27/3/0; minor/major 3/0) | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 1/0) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **97%** cov 100% (c/i/r 116/4/0; minor/major 4/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| opus | complete_unit | 3 | 3 | 0 | edition_variant 2, omission 1, addition 2 |
| opus | retrieve_quote | 1 | 1 | 0 | edition_variant 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| opus | Christianity | 100% cov 100% (n=30; c/i/r 30/0/0) | 90% cov 100% (n=30; c/i/r 27/3/0) | 97% cov 100% (n=30; c/i/r 29/1/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **97%** cov 100% (n=120; c/i/r 116/4/0) |

### By text (one text = one work · version · language)

**opus**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (NRSV, en) | 120 | 97% | 100% | 0 | — | 4 | 0 | edition_variant 3, omission 1, addition 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| opus | 120 | 9,947 | 17,130 |
| **total** | 120 | 9,947 | 17,130 |
