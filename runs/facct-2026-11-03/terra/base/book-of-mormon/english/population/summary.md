| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| terra | 73% cov 100% (n=30; c/i/r 22/8/0; minor/major 0/8) | 57% cov 100% (n=30; c/i/r 17/13/0; minor/major 8/5) | 47% cov 100% (n=30; c/i/r 14/16/0; minor/major 6/10) | 93% cov 100% (n=30; c/i/r 28/2/0; minor/major 0/2) | **68%** cov 100% (c/i/r 81/39/0; minor/major 14/25) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| terra | cite_passage | 8 | 0 | 8 | wrong_locus 8 |
| terra | complete_unit | 13 | 8 | 5 | edition_variant 4, wrong_passage 5, omission 4 |
| terra | retrieve_quote | 16 | 6 | 10 | edition_variant 1, paraphrase 5, wrong_passage 10, addition 2 |
| terra | verify_source | 2 | 0 | 2 | wrong_verdict 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| terra | Book of Mormon | 73% cov 100% (n=30; c/i/r 22/8/0) | 57% cov 100% (n=30; c/i/r 17/13/0) | 47% cov 100% (n=30; c/i/r 14/16/0) | 93% cov 100% (n=30; c/i/r 28/2/0) | **68%** cov 100% (n=120; c/i/r 81/39/0) |

### By text (one text = one work · version · language)

**terra**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Book of Mormon (2013 edition, en) | 120 | 68% | 100% | 0 | — | 14 | 25 | edition_variant 5, paraphrase 5, wrong_passage 15, omission 4, addition 2, wrong_locus 8, wrong_verdict 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| terra | 120 | 9,378 | 2,736 |
| **total** | 120 | 9,378 | 2,736 |
