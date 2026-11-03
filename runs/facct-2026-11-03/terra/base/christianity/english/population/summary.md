| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| terra | 93% cov 100% (n=30; c/i/r 28/2/0; minor/major 0/2) | 70% cov 100% (n=30; c/i/r 21/9/0; minor/major 8/1) | 67% cov 90% (n=30; c/i/r 18/9/3; minor/major 9/0) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **83%** cov 98% (c/i/r 97/20/3; minor/major 17/3) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| terra | cite_passage | 2 | 0 | 2 | wrong_locus 2 |
| terra | complete_unit | 9 | 8 | 1 | edition_variant 4, paraphrase 2, wrong_passage 1, omission 2, addition 2 |
| terra | retrieve_quote | 9 | 9 | 0 | edition_variant 4, near_copy 4, omission 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| terra | Christianity | 93% cov 100% (n=30; c/i/r 28/2/0) | 70% cov 100% (n=30; c/i/r 21/9/0) | 67% cov 90% (n=30; c/i/r 18/9/3) | 100% cov 100% (n=30; c/i/r 30/0/0) | **83%** cov 98% (n=120; c/i/r 97/20/3) |

### By text (one text = one work · version · language)

**terra**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (NRSV, en) | 120 | 83% | 98% | 3 | — | 17 | 3 | edition_variant 8, near_copy 4, paraphrase 2, wrong_passage 1, omission 3, addition 2, wrong_locus 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| terra | 120 | 6,864 | 2,259 |
| **total** | 120 | 6,864 | 2,259 |
