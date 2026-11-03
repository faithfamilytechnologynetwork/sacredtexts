| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| argon | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | 77% cov 100% (n=30; c/i/r 23/7/0; minor/major 6/1) | 53% cov 100% (n=30; c/i/r 16/14/0; minor/major 13/1) | 100% cov 97% (n=30; c/i/r 29/0/1; minor/major 0/0) | **82%** cov 99% (c/i/r 97/22/1; minor/major 19/3) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| argon | cite_passage | 1 | 0 | 1 | wrong_locus 1 |
| argon | complete_unit | 7 | 6 | 1 | edition_variant 2, paraphrase 4, wrong_passage 1 |
| argon | retrieve_quote | 14 | 13 | 1 | diacritic_only 2, edition_variant 9, paraphrase 1, wrong_passage 1, omission 1, addition 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| argon | Buddhism | 97% cov 100% (n=30; c/i/r 29/1/0) | 77% cov 100% (n=30; c/i/r 23/7/0) | 53% cov 100% (n=30; c/i/r 16/14/0) | 100% cov 97% (n=30; c/i/r 29/0/1) | **82%** cov 99% (n=120; c/i/r 97/22/1) |

### By text (one text = one work · version · language)

**argon**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Dhammapada (Chaṭṭha Saṅgāyana (VRI), pi) | 120 | 82% | 99% | 1 | — | 19 | 3 | diacritic_only 2, edition_variant 11, paraphrase 5, wrong_passage 2, omission 1, addition 1, wrong_locus 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| argon | 120 | 16,597 | 4,759 |
| **total** | 120 | 16,597 | 4,759 |
