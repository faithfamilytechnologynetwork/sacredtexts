| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| luna | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 43% cov 100% (n=30; c/i/r 13/17/0; minor/major 10/7) | 7% cov 93% (n=30; c/i/r 2/26/2; minor/major 0/26) | 83% cov 100% (n=30; c/i/r 25/5/0; minor/major 0/5) | **59%** cov 98% (c/i/r 70/48/2; minor/major 10/38) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| luna | complete_unit | 17 | 10 | 7 | paraphrase 8, wrong_passage 7, omission 2 |
| luna | retrieve_quote | 26 | 0 | 26 | wrong_passage 26 |
| luna | verify_source | 5 | 0 | 5 | wrong_verdict 5 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| luna | Hinduism | 100% cov 100% (n=30; c/i/r 30/0/0) | 43% cov 100% (n=30; c/i/r 13/17/0) | 7% cov 93% (n=30; c/i/r 2/26/2) | 83% cov 100% (n=30; c/i/r 25/5/0) | **59%** cov 98% (n=120; c/i/r 70/48/2) |

### By text (one text = one work · version · language)

**luna**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 59% | 98% | 2 | — | 10 | 38 | paraphrase 8, wrong_passage 33, omission 2, wrong_verdict 5 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| luna | 120 | 11,832 | 2,746 |
| **total** | 120 | 11,832 | 2,746 |
