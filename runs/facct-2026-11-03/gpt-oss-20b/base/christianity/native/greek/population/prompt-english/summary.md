| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gpt-oss-20b | 0% cov 100% (n=9; c/i/r 0/9/0; minor/major 0/9) | 0% cov 100% (n=9; c/i/r 0/9/0; minor/major 0/9) | 0% cov 100% (n=9; c/i/r 0/9/0; minor/major 0/9) | 56% cov 100% (n=9; c/i/r 5/4/0; minor/major 0/4) | **14%** cov 100% (c/i/r 5/31/0; minor/major 0/31) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gpt-oss-20b | cite_passage | 9 | 0 | 9 | wrong_locus 8, no_citation 1 |
| gpt-oss-20b | complete_unit | 9 | 0 | 9 | wrong_passage 9 |
| gpt-oss-20b | retrieve_quote | 9 | 0 | 9 | wrong_passage 9 |
| gpt-oss-20b | verify_source | 4 | 0 | 4 | wrong_verdict 4 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gpt-oss-20b | Christianity | 0% cov 100% (n=9; c/i/r 0/9/0) | 0% cov 100% (n=9; c/i/r 0/9/0) | 0% cov 100% (n=9; c/i/r 0/9/0) | 56% cov 100% (n=9; c/i/r 5/4/0) | **14%** cov 100% (n=36; c/i/r 5/31/0) |

### By text (one text = one work · version · language)

**gpt-oss-20b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (the Greek New Testament (Scrivener 1894), grc) | 36 | 14% | 100% | 0 | — | 0 | 31 | wrong_passage 18, wrong_locus 8, no_citation 1, wrong_verdict 4 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gpt-oss-20b | 36 | 6,081 | 70,213 |
| **total** | 36 | 6,081 | 70,213 |
