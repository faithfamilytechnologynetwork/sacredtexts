| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| kimi | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | 43% cov 100% (n=30; c/i/r 13/17/0; minor/major 13/4) | 50% cov 67% (n=30; c/i/r 10/10/10; minor/major 3/7) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **75%** cov 92% (c/i/r 82/28/10; minor/major 16/12) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| kimi | cite_passage | 1 | 0 | 1 | wrong_locus 1 |
| kimi | complete_unit | 17 | 13 | 4 | diacritic_only 2, paraphrase 7, wrong_passage 4, omission 4 |
| kimi | retrieve_quote | 10 | 3 | 7 | paraphrase 3, wrong_passage 7, addition 10 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| kimi | Hinduism | 97% cov 100% (n=30; c/i/r 29/1/0) | 43% cov 100% (n=30; c/i/r 13/17/0) | 50% cov 67% (n=30; c/i/r 10/10/10) | 100% cov 100% (n=30; c/i/r 30/0/0) | **75%** cov 92% (n=120; c/i/r 82/28/10) |

### By text (one text = one work · version · language)

**kimi**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 75% | 92% | 10 | — | 16 | 12 | diacritic_only 2, paraphrase 10, wrong_passage 11, omission 4, addition 10, wrong_locus 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| kimi | 120 | 13,775 | 6,416 |
| **total** | 120 | 13,775 | 6,416 |
