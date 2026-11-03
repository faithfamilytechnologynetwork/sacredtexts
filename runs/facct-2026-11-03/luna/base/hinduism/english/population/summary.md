| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| luna | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 25/5) | 0% cov 43% (n=30; c/i/r 0/13/17; minor/major 0/13) | 90% cov 100% (n=30; c/i/r 27/3/0; minor/major 0/3) | **55%** cov 86% (c/i/r 57/46/17; minor/major 25/21) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| luna | complete_unit | 30 | 25 | 5 | edition_variant 2, paraphrase 23, wrong_passage 5 |
| luna | retrieve_quote | 13 | 0 | 13 | wrong_passage 13 |
| luna | verify_source | 3 | 0 | 3 | wrong_verdict 3 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| luna | Hinduism | 100% cov 100% (n=30; c/i/r 30/0/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 43% (n=30; c/i/r 0/13/17) | 90% cov 100% (n=30; c/i/r 27/3/0) | **55%** cov 86% (n=120; c/i/r 57/46/17) |

### By text (one text = one work · version · language)

**luna**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Annie Besant (1922), en) | 120 | 55% | 86% | 17 | — | 25 | 21 | edition_variant 2, paraphrase 23, wrong_passage 18, wrong_verdict 3 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| luna | 120 | 7,938 | 1,857 |
| **total** | 120 | 7,938 | 1,857 |
