| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemini-flash | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 53% cov 100% (n=30; c/i/r 16/14/0; minor/major 12/2) | 30% cov 100% (n=30; c/i/r 9/21/0; minor/major 21/0) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **71%** cov 100% (c/i/r 85/35/0; minor/major 33/2) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gemini-flash | complete_unit | 14 | 12 | 2 | diacritic_only 5, edition_variant 2, paraphrase 5, wrong_passage 2, addition 1 |
| gemini-flash | retrieve_quote | 21 | 21 | 0 | diacritic_only 3, edition_variant 12, near_copy 1, paraphrase 4, omission 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemini-flash | Buddhism | 100% cov 100% (n=30; c/i/r 30/0/0) | 53% cov 100% (n=30; c/i/r 16/14/0) | 30% cov 100% (n=30; c/i/r 9/21/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **71%** cov 100% (n=120; c/i/r 85/35/0) |

### By text (one text = one work · version · language)

**gemini-flash**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Dhammapada (Chaṭṭha Saṅgāyana (VRI), pi) | 120 | 71% | 100% | 0 | — | 33 | 2 | diacritic_only 8, edition_variant 14, near_copy 1, paraphrase 9, wrong_passage 2, omission 1, addition 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemini-flash | 120 | 12,666 | 26,938 |
| **total** | 120 | 12,666 | 26,938 |
