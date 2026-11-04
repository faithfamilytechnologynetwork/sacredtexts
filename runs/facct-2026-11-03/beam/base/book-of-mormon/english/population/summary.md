| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| beam | 67% cov 100% (n=30; c/i/r 20/10/0; minor/major 0/10) | 43% cov 100% (n=30; c/i/r 13/17/0; minor/major 8/9) | 67% cov 30% (n=30; c/i/r 6/3/21; minor/major 2/1) | 90% cov 100% (n=30; c/i/r 27/3/0; minor/major 0/3) | **67%** cov 82% (c/i/r 66/33/21; minor/major 10/23) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| beam | cite_passage | 10 | 0 | 10 | wrong_locus 10 |
| beam | complete_unit | 17 | 8 | 9 | near_copy 2, paraphrase 3, wrong_passage 9, omission 3 |
| beam | retrieve_quote | 3 | 2 | 1 | edition_variant 2, wrong_passage 1 |
| beam | verify_source | 3 | 0 | 3 | wrong_verdict 3 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| beam | Book of Mormon | 67% cov 100% (n=30; c/i/r 20/10/0) | 43% cov 100% (n=30; c/i/r 13/17/0) | 67% cov 30% (n=30; c/i/r 6/3/21) | 90% cov 100% (n=30; c/i/r 27/3/0) | **67%** cov 82% (n=120; c/i/r 66/33/21) |

### By text (one text = one work · version · language)

**beam**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Book of Mormon (2013 edition, en) | 120 | 67% | 82% | 21 | — | 10 | 23 | edition_variant 2, near_copy 2, paraphrase 3, wrong_passage 10, omission 3, wrong_locus 10, wrong_verdict 3 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| beam | 120 | 14,441 | 116,089 |
| **total** | 120 | 14,441 | 116,089 |
