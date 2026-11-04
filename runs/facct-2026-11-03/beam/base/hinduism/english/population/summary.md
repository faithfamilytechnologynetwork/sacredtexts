| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| beam | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | 3% cov 100% (n=30; c/i/r 1/29/0; minor/major 23/6) | 0% cov 77% (n=30; c/i/r 0/23/7; minor/major 21/2) | 90% cov 100% (n=30; c/i/r 27/3/0; minor/major 0/3) | **50%** cov 94% (c/i/r 57/56/7; minor/major 44/12) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| beam | cite_passage | 1 | 0 | 1 | wrong_locus 1 |
| beam | complete_unit | 29 | 23 | 6 | edition_variant 2, near_copy 1, paraphrase 20, wrong_passage 6 |
| beam | retrieve_quote | 23 | 21 | 2 | near_copy 1, paraphrase 20, wrong_passage 2 |
| beam | verify_source | 3 | 0 | 3 | wrong_verdict 3 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| beam | Hinduism | 97% cov 100% (n=30; c/i/r 29/1/0) | 3% cov 100% (n=30; c/i/r 1/29/0) | 0% cov 77% (n=30; c/i/r 0/23/7) | 90% cov 100% (n=30; c/i/r 27/3/0) | **50%** cov 94% (n=120; c/i/r 57/56/7) |

### By text (one text = one work · version · language)

**beam**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Annie Besant (1922), en) | 120 | 50% | 94% | 7 | — | 44 | 12 | edition_variant 2, near_copy 2, paraphrase 40, wrong_passage 8, wrong_locus 1, wrong_verdict 3 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| beam | 120 | 13,126 | 89,573 |
| **total** | 120 | 13,126 | 89,573 |
