| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| luna | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 33% cov 100% (n=30; c/i/r 10/20/0; minor/major 12/8) | 27% cov 73% (n=30; c/i/r 6/16/8; minor/major 8/8) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **68%** cov 93% (c/i/r 76/36/8; minor/major 20/16) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| luna | complete_unit | 20 | 12 | 8 | diacritic_only 1, edition_variant 1, paraphrase 6, wrong_passage 8, omission 4 |
| luna | retrieve_quote | 16 | 8 | 8 | edition_variant 1, near_copy 1, paraphrase 6, wrong_passage 8, addition 3 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| luna | Hinduism | 100% cov 100% (n=30; c/i/r 30/0/0) | 33% cov 100% (n=30; c/i/r 10/20/0) | 27% cov 73% (n=30; c/i/r 6/16/8) | 100% cov 100% (n=30; c/i/r 30/0/0) | **68%** cov 93% (n=120; c/i/r 76/36/8) |

### By text (one text = one work · version · language)

**luna**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 68% | 93% | 8 | — | 20 | 16 | diacritic_only 1, edition_variant 2, near_copy 1, paraphrase 12, wrong_passage 16, omission 4, addition 3 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| luna | 120 | 9,289 | 2,796 |
| **total** | 120 | 9,289 | 2,796 |
