| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sol | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | 67% cov 100% (n=30; c/i/r 20/10/0; minor/major 10/0) | 37% cov 100% (n=30; c/i/r 11/19/0; minor/major 19/0) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **75%** cov 100% (c/i/r 90/30/0; minor/major 29/1) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sol | cite_passage | 1 | 0 | 1 | wrong_locus 1 |
| sol | complete_unit | 10 | 10 | 0 | edition_variant 2, near_copy 2, paraphrase 6, addition 1 |
| sol | retrieve_quote | 19 | 19 | 0 | edition_variant 1, near_copy 9, paraphrase 9 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sol | Hinduism | 97% cov 100% (n=30; c/i/r 29/1/0) | 67% cov 100% (n=30; c/i/r 20/10/0) | 37% cov 100% (n=30; c/i/r 11/19/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **75%** cov 100% (n=120; c/i/r 90/30/0) |

### By text (one text = one work · version · language)

**sol**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Annie Besant (1922), en) | 120 | 75% | 100% | 0 | — | 29 | 1 | edition_variant 3, near_copy 11, paraphrase 15, addition 1, wrong_locus 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sol | 120 | 7,938 | 17,294 |
| **total** | 120 | 7,938 | 17,294 |
