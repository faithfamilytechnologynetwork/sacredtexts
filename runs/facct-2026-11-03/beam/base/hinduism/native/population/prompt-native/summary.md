| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| beam | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 83% cov 100% (n=30; c/i/r 25/5/0; minor/major 4/1) | 59% cov 97% (n=30; c/i/r 17/12/1; minor/major 10/2) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **86%** cov 99% (c/i/r 102/17/1; minor/major 14/3) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| beam | complete_unit | 5 | 4 | 1 | edition_variant 1, paraphrase 3, wrong_passage 1 |
| beam | retrieve_quote | 12 | 10 | 2 | edition_variant 2, paraphrase 8, wrong_passage 2, addition 7 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| beam | Hinduism | 100% cov 100% (n=30; c/i/r 30/0/0) | 83% cov 100% (n=30; c/i/r 25/5/0) | 59% cov 97% (n=30; c/i/r 17/12/1) | 100% cov 100% (n=30; c/i/r 30/0/0) | **86%** cov 99% (n=120; c/i/r 102/17/1) |

### By text (one text = one work · version · language)

**beam**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 86% | 99% | 1 | — | 14 | 3 | edition_variant 3, paraphrase 11, wrong_passage 3, addition 7 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| beam | 120 | 22,643 | 80,114 |
| **total** | 120 | 22,643 | 80,114 |
