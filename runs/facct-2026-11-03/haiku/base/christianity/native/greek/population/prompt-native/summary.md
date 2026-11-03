| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| haiku | 100% cov 100% (n=9; c/i/r 9/0/0; minor/major 0/0) | 22% cov 100% (n=9; c/i/r 2/7/0; minor/major 6/1) | n/a cov 0% (n=9; c/i/r 0/0/9; minor/major 0/0) | 100% cov 44% (n=9; c/i/r 4/0/5; minor/major 0/0) | **68%** cov 61% (c/i/r 15/7/14; minor/major 6/1) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| haiku | complete_unit | 7 | 6 | 1 | edition_variant 2, paraphrase 4, wrong_passage 1, addition 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| haiku | Christianity | 100% cov 100% (n=9; c/i/r 9/0/0) | 22% cov 100% (n=9; c/i/r 2/7/0) | n/a cov 0% (n=9; c/i/r 0/0/9) | 100% cov 44% (n=9; c/i/r 4/0/5) | **68%** cov 61% (n=36; c/i/r 15/7/14) |

### By text (one text = one work · version · language)

**haiku**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (the Greek New Testament (Scrivener 1894), grc) | 36 | 68% | 61% | 14 | — | 6 | 1 | edition_variant 2, paraphrase 4, wrong_passage 1, addition 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| haiku | 36 | 5,712 | 8,976 |
| **total** | 36 | 5,712 | 8,976 |
