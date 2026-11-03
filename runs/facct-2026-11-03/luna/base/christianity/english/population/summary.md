| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| luna | 93% cov 100% (n=30; c/i/r 28/2/0; minor/major 0/2) | 53% cov 100% (n=30; c/i/r 16/14/0; minor/major 11/3) | 40% cov 33% (n=30; c/i/r 4/6/20; minor/major 4/2) | 90% cov 100% (n=30; c/i/r 27/3/0; minor/major 0/3) | **75%** cov 83% (c/i/r 75/25/20; minor/major 15/10) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| luna | cite_passage | 2 | 0 | 2 | wrong_locus 2 |
| luna | complete_unit | 14 | 11 | 3 | edition_variant 4, near_copy 1, paraphrase 5, wrong_passage 3, omission 1, addition 1 |
| luna | retrieve_quote | 6 | 4 | 2 | edition_variant 3, wrong_passage 2, omission 1, addition 1 |
| luna | verify_source | 3 | 0 | 3 | wrong_verdict 3 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| luna | Christianity | 93% cov 100% (n=30; c/i/r 28/2/0) | 53% cov 100% (n=30; c/i/r 16/14/0) | 40% cov 33% (n=30; c/i/r 4/6/20) | 90% cov 100% (n=30; c/i/r 27/3/0) | **75%** cov 83% (n=120; c/i/r 75/25/20) |

### By text (one text = one work · version · language)

**luna**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (NRSV, en) | 120 | 75% | 83% | 20 | — | 15 | 10 | edition_variant 7, near_copy 1, paraphrase 5, wrong_passage 5, omission 2, addition 2, wrong_locus 2, wrong_verdict 3 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| luna | 120 | 6,864 | 2,226 |
| **total** | 120 | 6,864 | 2,226 |
