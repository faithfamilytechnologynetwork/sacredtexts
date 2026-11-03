| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| kimi | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | 40% cov 100% (n=30; c/i/r 12/18/0; minor/major 14/4) | 35% cov 67% (n=30; c/i/r 7/13/10; minor/major 6/7) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **71%** cov 92% (c/i/r 78/32/10; minor/major 20/12) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| kimi | cite_passage | 1 | 0 | 1 | wrong_locus 1 |
| kimi | complete_unit | 18 | 14 | 4 | diacritic_only 2, edition_variant 1, paraphrase 7, wrong_passage 4, omission 4 |
| kimi | retrieve_quote | 13 | 6 | 7 | paraphrase 6, wrong_passage 7, addition 7 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| kimi | Hinduism | 97% cov 100% (n=30; c/i/r 29/1/0) | 40% cov 100% (n=30; c/i/r 12/18/0) | 35% cov 67% (n=30; c/i/r 7/13/10) | 100% cov 100% (n=30; c/i/r 30/0/0) | **71%** cov 92% (n=120; c/i/r 78/32/10) |

### By text (one text = one work · version · language)

**kimi**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 71% | 92% | 10 | — | 20 | 12 | diacritic_only 2, edition_variant 1, paraphrase 13, wrong_passage 11, omission 4, addition 7, wrong_locus 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| kimi | 120 | 13,775 | 6,416 |
| **total** | 120 | 13,775 | 6,416 |
