| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| beam | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | 80% cov 100% (n=30; c/i/r 24/6/0; minor/major 5/1) | 62% cov 97% (n=30; c/i/r 18/11/1; minor/major 11/0) | 90% cov 100% (n=30; c/i/r 27/3/0; minor/major 0/3) | **82%** cov 99% (c/i/r 98/21/1; minor/major 16/5) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| beam | cite_passage | 1 | 0 | 1 | wrong_locus 1 |
| beam | complete_unit | 6 | 5 | 1 | paraphrase 5, wrong_passage 1 |
| beam | retrieve_quote | 11 | 11 | 0 | edition_variant 2, paraphrase 9 |
| beam | verify_source | 3 | 0 | 3 | wrong_verdict 3 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| beam | Hinduism | 97% cov 100% (n=30; c/i/r 29/1/0) | 80% cov 100% (n=30; c/i/r 24/6/0) | 62% cov 97% (n=30; c/i/r 18/11/1) | 90% cov 100% (n=30; c/i/r 27/3/0) | **82%** cov 99% (n=120; c/i/r 98/21/1) |

### By text (one text = one work · version · language)

**beam**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 82% | 99% | 1 | — | 16 | 5 | edition_variant 2, paraphrase 14, wrong_passage 1, wrong_locus 1, wrong_verdict 3 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| beam | 120 | 19,995 | 104,241 |
| **total** | 120 | 19,995 | 104,241 |
