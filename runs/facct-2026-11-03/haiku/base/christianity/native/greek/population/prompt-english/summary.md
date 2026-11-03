| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| haiku | 100% cov 100% (n=9; c/i/r 9/0/0; minor/major 0/0) | 33% cov 100% (n=9; c/i/r 3/6/0; minor/major 6/0) | 0% cov 100% (n=9; c/i/r 0/9/0; minor/major 9/0) | 100% cov 100% (n=9; c/i/r 9/0/0; minor/major 0/0) | **58%** cov 100% (c/i/r 21/15/0; minor/major 15/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| haiku | complete_unit | 6 | 6 | 0 | edition_variant 3, paraphrase 3 |
| haiku | retrieve_quote | 9 | 9 | 0 | edition_variant 6, near_copy 2, paraphrase 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| haiku | Christianity | 100% cov 100% (n=9; c/i/r 9/0/0) | 33% cov 100% (n=9; c/i/r 3/6/0) | 0% cov 100% (n=9; c/i/r 0/9/0) | 100% cov 100% (n=9; c/i/r 9/0/0) | **58%** cov 100% (n=36; c/i/r 21/15/0) |

### By text (one text = one work · version · language)

**haiku**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (the Greek New Testament (Scrivener 1894), grc) | 36 | 58% | 100% | 0 | — | 15 | 0 | edition_variant 9, near_copy 2, paraphrase 4 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| haiku | 36 | 5,273 | 1,927 |
| **total** | 36 | 5,273 | 1,927 |
