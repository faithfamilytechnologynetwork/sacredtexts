| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sonnet | 100% cov 100% (n=9; c/i/r 9/0/0; minor/major 0/0) | 78% cov 100% (n=9; c/i/r 7/2/0; minor/major 1/1) | 56% cov 100% (n=9; c/i/r 5/4/0; minor/major 4/0) | 100% cov 67% (n=9; c/i/r 6/0/3; minor/major 0/0) | **82%** cov 92% (c/i/r 27/6/3; minor/major 5/1) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sonnet | complete_unit | 2 | 1 | 1 | paraphrase 1, wrong_passage 1, addition 7 |
| sonnet | retrieve_quote | 4 | 4 | 0 | edition_variant 4, addition 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sonnet | Christianity | 100% cov 100% (n=9; c/i/r 9/0/0) | 78% cov 100% (n=9; c/i/r 7/2/0) | 56% cov 100% (n=9; c/i/r 5/4/0) | 100% cov 67% (n=9; c/i/r 6/0/3) | **82%** cov 92% (n=36; c/i/r 27/6/3) |

### By text (one text = one work · version · language)

**sonnet**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (the Greek New Testament (Scrivener 1894), grc) | 36 | 82% | 92% | 3 | — | 5 | 1 | edition_variant 4, paraphrase 1, wrong_passage 1, addition 9 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sonnet | 36 | 5,345 | 6,851 |
| **total** | 36 | 5,345 | 6,851 |
