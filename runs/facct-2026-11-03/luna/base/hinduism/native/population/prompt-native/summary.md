| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| luna | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 40% cov 100% (n=30; c/i/r 12/18/0; minor/major 10/8) | 32% cov 73% (n=30; c/i/r 7/15/8; minor/major 7/8) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **71%** cov 93% (c/i/r 79/33/8; minor/major 17/16) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| luna | complete_unit | 18 | 10 | 8 | diacritic_only 1, paraphrase 5, wrong_passage 8, omission 4 |
| luna | retrieve_quote | 15 | 7 | 8 | edition_variant 1, near_copy 1, paraphrase 5, wrong_passage 8, addition 4 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| luna | Hinduism | 100% cov 100% (n=30; c/i/r 30/0/0) | 40% cov 100% (n=30; c/i/r 12/18/0) | 32% cov 73% (n=30; c/i/r 7/15/8) | 100% cov 100% (n=30; c/i/r 30/0/0) | **71%** cov 93% (n=120; c/i/r 79/33/8) |

### By text (one text = one work · version · language)

**luna**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 71% | 93% | 8 | — | 17 | 16 | diacritic_only 1, edition_variant 1, near_copy 1, paraphrase 10, wrong_passage 16, omission 4, addition 4 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| luna | 120 | 9,289 | 2,796 |
| **total** | 120 | 9,289 | 2,796 |
