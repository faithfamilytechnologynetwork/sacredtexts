| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| kimi | 93% cov 100% (n=30; c/i/r 28/2/0; minor/major 0/2) | 33% cov 100% (n=30; c/i/r 10/20/0; minor/major 16/4) | 34% cov 97% (n=30; c/i/r 10/19/1; minor/major 9/10) | 67% cov 100% (n=30; c/i/r 20/10/0; minor/major 0/10) | **57%** cov 99% (c/i/r 68/51/1; minor/major 25/26) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| kimi | cite_passage | 2 | 0 | 2 | wrong_locus 2 |
| kimi | complete_unit | 20 | 16 | 4 | edition_variant 5, near_copy 1, paraphrase 10, wrong_passage 4 |
| kimi | retrieve_quote | 19 | 9 | 10 | diacritic_only 3, edition_variant 3, paraphrase 3, wrong_passage 10 |
| kimi | verify_source | 10 | 0 | 10 | wrong_verdict 10 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| kimi | Buddhism | 93% cov 100% (n=30; c/i/r 28/2/0) | 33% cov 100% (n=30; c/i/r 10/20/0) | 34% cov 97% (n=30; c/i/r 10/19/1) | 67% cov 100% (n=30; c/i/r 20/10/0) | **57%** cov 99% (n=120; c/i/r 68/51/1) |

### By text (one text = one work · version · language)

**kimi**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Dhammapada (Chaṭṭha Saṅgāyana (VRI), pi) | 120 | 57% | 99% | 1 | — | 25 | 26 | diacritic_only 3, edition_variant 8, near_copy 1, paraphrase 13, wrong_passage 14, wrong_locus 2, wrong_verdict 10 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| kimi | 120 | 16,986 | 4,208 |
| **total** | 120 | 16,986 | 4,208 |
