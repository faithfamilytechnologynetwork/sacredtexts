| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| kimi | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 53% cov 100% (n=30; c/i/r 16/14/0; minor/major 12/2) | 23% cov 100% (n=30; c/i/r 7/23/0; minor/major 4/19) | 93% cov 93% (n=30; c/i/r 26/2/2; minor/major 0/2) | **67%** cov 98% (c/i/r 79/39/2; minor/major 16/23) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| kimi | complete_unit | 14 | 12 | 2 | diacritic_only 1, edition_variant 1, paraphrase 9, wrong_passage 2, omission 1 |
| kimi | retrieve_quote | 23 | 4 | 19 | edition_variant 1, paraphrase 3, wrong_passage 19 |
| kimi | verify_source | 2 | 0 | 2 | wrong_verdict 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| kimi | Hinduism | 100% cov 100% (n=30; c/i/r 30/0/0) | 53% cov 100% (n=30; c/i/r 16/14/0) | 23% cov 100% (n=30; c/i/r 7/23/0) | 93% cov 93% (n=30; c/i/r 26/2/2) | **67%** cov 98% (n=120; c/i/r 79/39/2) |

### By text (one text = one work · version · language)

**kimi**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 67% | 98% | 2 | — | 16 | 23 | diacritic_only 1, edition_variant 2, paraphrase 12, wrong_passage 21, omission 1, wrong_verdict 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| kimi | 120 | 14,630 | 5,412 |
| **total** | 120 | 14,630 | 5,412 |
