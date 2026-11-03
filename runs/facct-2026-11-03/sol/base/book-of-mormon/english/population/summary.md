| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sol | 93% cov 100% (n=30; c/i/r 28/2/0; minor/major 0/2) | 90% cov 100% (n=30; c/i/r 27/3/0; minor/major 1/2) | 93% cov 100% (n=30; c/i/r 28/2/0; minor/major 2/0) | 90% cov 100% (n=30; c/i/r 27/3/0; minor/major 0/3) | **92%** cov 100% (c/i/r 110/10/0; minor/major 3/7) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sol | cite_passage | 2 | 0 | 2 | wrong_locus 2 |
| sol | complete_unit | 3 | 1 | 2 | paraphrase 1, wrong_passage 2, addition 1 |
| sol | retrieve_quote | 2 | 2 | 0 | edition_variant 1, paraphrase 1 |
| sol | verify_source | 3 | 0 | 3 | wrong_verdict 3 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sol | Book of Mormon | 93% cov 100% (n=30; c/i/r 28/2/0) | 90% cov 100% (n=30; c/i/r 27/3/0) | 93% cov 100% (n=30; c/i/r 28/2/0) | 90% cov 100% (n=30; c/i/r 27/3/0) | **92%** cov 100% (n=120; c/i/r 110/10/0) |

### By text (one text = one work · version · language)

**sol**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Book of Mormon (2013 edition, en) | 120 | 92% | 100% | 0 | — | 3 | 7 | edition_variant 1, paraphrase 2, wrong_passage 2, addition 1, wrong_locus 2, wrong_verdict 3 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sol | 120 | 9,378 | 16,928 |
| **total** | 120 | 9,378 | 16,928 |
