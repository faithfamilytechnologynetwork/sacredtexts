| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| deepseek-v4-pro | 90% cov 100% (n=30; c/i/r 27/3/0; minor/major 0/3) | 27% cov 100% (n=30; c/i/r 8/22/0; minor/major 18/4) | 20% cov 100% (n=30; c/i/r 6/24/0; minor/major 13/11) | 87% cov 100% (n=30; c/i/r 26/4/0; minor/major 0/4) | **56%** cov 100% (c/i/r 67/53/0; minor/major 31/22) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| deepseek-v4-pro | cite_passage | 3 | 0 | 3 | wrong_locus 3 |
| deepseek-v4-pro | complete_unit | 22 | 18 | 4 | edition_variant 5, paraphrase 10, wrong_passage 4, omission 3 |
| deepseek-v4-pro | retrieve_quote | 24 | 13 | 11 | diacritic_only 2, edition_variant 4, paraphrase 7, wrong_passage 11 |
| deepseek-v4-pro | verify_source | 4 | 0 | 4 | wrong_verdict 4 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| deepseek-v4-pro | Buddhism | 90% cov 100% (n=30; c/i/r 27/3/0) | 27% cov 100% (n=30; c/i/r 8/22/0) | 20% cov 100% (n=30; c/i/r 6/24/0) | 87% cov 100% (n=30; c/i/r 26/4/0) | **56%** cov 100% (n=120; c/i/r 67/53/0) |

### By text (one text = one work · version · language)

**deepseek-v4-pro**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Dhammapada (Chaṭṭha Saṅgāyana (VRI), pi) | 120 | 56% | 100% | 0 | — | 31 | 22 | diacritic_only 2, edition_variant 9, paraphrase 17, wrong_passage 15, omission 3, wrong_locus 3, wrong_verdict 4 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| deepseek-v4-pro | 120 | 14,458 | 2,951 |
| **total** | 120 | 14,458 | 2,951 |
