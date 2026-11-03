| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| terra | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | 67% cov 100% (n=30; c/i/r 20/10/0; minor/major 7/3) | 50% cov 100% (n=30; c/i/r 15/15/0; minor/major 14/1) | 93% cov 100% (n=30; c/i/r 28/2/0; minor/major 0/2) | **77%** cov 100% (c/i/r 92/28/0; minor/major 21/7) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| terra | cite_passage | 1 | 0 | 1 | wrong_locus 1 |
| terra | complete_unit | 10 | 7 | 3 | diacritic_only 1, edition_variant 2, paraphrase 3, wrong_passage 3, omission 1 |
| terra | retrieve_quote | 15 | 14 | 1 | diacritic_only 1, edition_variant 8, near_copy 1, paraphrase 4, wrong_passage 1 |
| terra | verify_source | 2 | 0 | 2 | wrong_verdict 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| terra | Buddhism | 97% cov 100% (n=30; c/i/r 29/1/0) | 67% cov 100% (n=30; c/i/r 20/10/0) | 50% cov 100% (n=30; c/i/r 15/15/0) | 93% cov 100% (n=30; c/i/r 28/2/0) | **77%** cov 100% (n=120; c/i/r 92/28/0) |

### By text (one text = one work · version · language)

**terra**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Dhammapada (Chaṭṭha Saṅgāyana (VRI), pi) | 120 | 77% | 100% | 0 | — | 21 | 7 | diacritic_only 2, edition_variant 10, near_copy 1, paraphrase 7, wrong_passage 4, omission 1, wrong_locus 1, wrong_verdict 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| terra | 120 | 13,878 | 3,421 |
| **total** | 120 | 13,878 | 3,421 |
