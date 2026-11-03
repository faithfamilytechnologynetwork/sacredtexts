| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| terra | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 60% cov 100% (n=30; c/i/r 18/12/0; minor/major 9/3) | 57% cov 100% (n=30; c/i/r 17/13/0; minor/major 12/1) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **79%** cov 100% (c/i/r 95/25/0; minor/major 21/4) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| terra | complete_unit | 12 | 9 | 3 | edition_variant 1, paraphrase 6, wrong_passage 3, omission 2 |
| terra | retrieve_quote | 13 | 12 | 1 | edition_variant 3, paraphrase 9, wrong_passage 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| terra | Hinduism | 100% cov 100% (n=30; c/i/r 30/0/0) | 60% cov 100% (n=30; c/i/r 18/12/0) | 57% cov 100% (n=30; c/i/r 17/13/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **79%** cov 100% (n=120; c/i/r 95/25/0) |

### By text (one text = one work · version · language)

**terra**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 79% | 100% | 0 | — | 21 | 4 | edition_variant 4, paraphrase 15, wrong_passage 4, omission 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| terra | 120 | 9,289 | 2,669 |
| **total** | 120 | 9,289 | 2,669 |
