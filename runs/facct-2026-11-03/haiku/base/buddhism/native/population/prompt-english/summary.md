| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| haiku | 80% cov 100% (n=30; c/i/r 24/6/0; minor/major 0/6) | 20% cov 100% (n=30; c/i/r 6/24/0; minor/major 12/12) | 0% cov 13% (n=30; c/i/r 0/4/26; minor/major 1/3) | 95% cov 73% (n=30; c/i/r 21/1/8; minor/major 0/1) | **59%** cov 72% (c/i/r 51/35/34; minor/major 13/22) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| haiku | cite_passage | 6 | 0 | 6 | wrong_locus 5, hedge 1 |
| haiku | complete_unit | 24 | 12 | 12 | edition_variant 2, paraphrase 10, wrong_passage 12, addition 1 |
| haiku | retrieve_quote | 4 | 1 | 3 | paraphrase 1, wrong_passage 3 |
| haiku | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| haiku | Buddhism | 80% cov 100% (n=30; c/i/r 24/6/0) | 20% cov 100% (n=30; c/i/r 6/24/0) | 0% cov 13% (n=30; c/i/r 0/4/26) | 95% cov 73% (n=30; c/i/r 21/1/8) | **59%** cov 72% (n=120; c/i/r 51/35/34) |

### By text (one text = one work · version · language)

**haiku**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Dhammapada (Chaṭṭha Saṅgāyana (VRI), pi) | 120 | 59% | 72% | 34 | — | 13 | 22 | edition_variant 2, paraphrase 11, wrong_passage 15, addition 1, wrong_locus 5, hedge 1, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| haiku | 120 | 20,554 | 13,173 |
| **total** | 120 | 20,554 | 13,173 |
