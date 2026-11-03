| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemma-31b | 3% cov 100% (n=30; c/i/r 1/29/0; minor/major 0/29) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 1/29) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 1/29) | 67% cov 70% (n=30; c/i/r 14/7/9; minor/major 0/7) | **14%** cov 92% (c/i/r 15/96/9; minor/major 2/94) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gemma-31b | cite_passage | 29 | 0 | 29 | wrong_locus 27, no_citation 2 |
| gemma-31b | complete_unit | 30 | 1 | 29 | paraphrase 1, wrong_passage 29 |
| gemma-31b | retrieve_quote | 30 | 1 | 29 | paraphrase 1, wrong_passage 29 |
| gemma-31b | verify_source | 7 | 0 | 7 | wrong_verdict 7 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemma-31b | Buddhism | 3% cov 100% (n=30; c/i/r 1/29/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 67% cov 70% (n=30; c/i/r 14/7/9) | **14%** cov 92% (n=120; c/i/r 15/96/9) |

### By text (one text = one work · version · language)

**gemma-31b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Dhammapada (Chaṭṭha Saṅgāyana (VRI), pi) | 120 | 14% | 92% | 9 | — | 2 | 94 | paraphrase 2, wrong_passage 58, wrong_locus 27, no_citation 2, wrong_verdict 7 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemma-31b | 120 | 14,222 | 14,598 |
| **total** | 120 | 14,222 | 14,598 |
