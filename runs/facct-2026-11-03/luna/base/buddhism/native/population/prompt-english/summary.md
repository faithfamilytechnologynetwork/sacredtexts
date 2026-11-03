| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| luna | 87% cov 100% (n=30; c/i/r 26/4/0; minor/major 0/4) | 27% cov 100% (n=30; c/i/r 8/22/0; minor/major 15/7) | 33% cov 100% (n=30; c/i/r 10/20/0; minor/major 7/13) | 48% cov 83% (n=30; c/i/r 12/13/5; minor/major 0/13) | **49%** cov 96% (c/i/r 56/59/5; minor/major 22/37) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| luna | cite_passage | 4 | 0 | 4 | wrong_locus 4 |
| luna | complete_unit | 22 | 15 | 7 | edition_variant 5, paraphrase 9, wrong_passage 7, omission 1 |
| luna | retrieve_quote | 20 | 7 | 13 | edition_variant 6, paraphrase 1, wrong_passage 13 |
| luna | verify_source | 13 | 0 | 13 | wrong_verdict 13 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| luna | Buddhism | 87% cov 100% (n=30; c/i/r 26/4/0) | 27% cov 100% (n=30; c/i/r 8/22/0) | 33% cov 100% (n=30; c/i/r 10/20/0) | 48% cov 83% (n=30; c/i/r 12/13/5) | **49%** cov 96% (n=120; c/i/r 56/59/5) |

### By text (one text = one work · version · language)

**luna**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Dhammapada (Chaṭṭha Saṅgāyana (VRI), pi) | 120 | 49% | 96% | 5 | — | 22 | 37 | edition_variant 11, paraphrase 10, wrong_passage 20, omission 1, wrong_locus 4, wrong_verdict 13 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| luna | 120 | 13,878 | 3,219 |
| **total** | 120 | 13,878 | 3,219 |
