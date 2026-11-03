| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| beam | 87% cov 100% (n=30; c/i/r 26/4/0; minor/major 0/4) | 37% cov 100% (n=30; c/i/r 11/19/0; minor/major 15/4) | 25% cov 93% (n=30; c/i/r 7/21/2; minor/major 4/17) | 93% cov 100% (n=30; c/i/r 28/2/0; minor/major 0/2) | **61%** cov 98% (c/i/r 72/46/2; minor/major 19/27) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| beam | cite_passage | 4 | 0 | 4 | wrong_locus 4 |
| beam | complete_unit | 19 | 15 | 4 | diacritic_only 1, edition_variant 5, paraphrase 9, wrong_passage 4 |
| beam | retrieve_quote | 21 | 4 | 17 | diacritic_only 1, edition_variant 1, near_copy 1, wrong_passage 17, omission 1 |
| beam | verify_source | 2 | 0 | 2 | wrong_verdict 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| beam | Buddhism | 87% cov 100% (n=30; c/i/r 26/4/0) | 37% cov 100% (n=30; c/i/r 11/19/0) | 25% cov 93% (n=30; c/i/r 7/21/2) | 93% cov 100% (n=30; c/i/r 28/2/0) | **61%** cov 98% (n=120; c/i/r 72/46/2) |

### By text (one text = one work · version · language)

**beam**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Dhammapada (Chaṭṭha Saṅgāyana (VRI), pi) | 120 | 61% | 98% | 2 | — | 19 | 27 | diacritic_only 2, edition_variant 6, near_copy 1, paraphrase 9, wrong_passage 21, omission 1, wrong_locus 4, wrong_verdict 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| beam | 120 | 20,016 | 154,023 |
| **total** | 120 | 20,016 | 154,023 |
