| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| kimi | 89% cov 100% (n=9; c/i/r 8/1/0; minor/major 0/1) | 67% cov 100% (n=9; c/i/r 6/3/0; minor/major 3/0) | 33% cov 100% (n=9; c/i/r 3/6/0; minor/major 6/0) | 100% cov 100% (n=9; c/i/r 9/0/0; minor/major 0/0) | **72%** cov 100% (c/i/r 26/10/0; minor/major 9/1) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| kimi | cite_passage | 1 | 0 | 1 | wrong_locus 1 |
| kimi | complete_unit | 3 | 3 | 0 | edition_variant 3 |
| kimi | retrieve_quote | 6 | 6 | 0 | edition_variant 4, near_copy 1, paraphrase 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| kimi | Christianity | 89% cov 100% (n=9; c/i/r 8/1/0) | 67% cov 100% (n=9; c/i/r 6/3/0) | 33% cov 100% (n=9; c/i/r 3/6/0) | 100% cov 100% (n=9; c/i/r 9/0/0) | **72%** cov 100% (n=36; c/i/r 26/10/0) |

### By text (one text = one work · version · language)

**kimi**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (the Greek New Testament (Scrivener 1894), grc) | 36 | 72% | 100% | 0 | — | 9 | 1 | edition_variant 7, near_copy 1, paraphrase 1, wrong_locus 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| kimi | 36 | 4,262 | 1,758 |
| **total** | 36 | 4,262 | 1,758 |
