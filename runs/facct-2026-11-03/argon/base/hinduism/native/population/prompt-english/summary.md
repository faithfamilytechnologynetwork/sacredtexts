| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| argon | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 80% cov 100% (n=30; c/i/r 24/6/0; minor/major 5/1) | 60% cov 100% (n=30; c/i/r 18/12/0; minor/major 12/0) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **85%** cov 100% (c/i/r 102/18/0; minor/major 17/1) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| argon | complete_unit | 6 | 5 | 1 | paraphrase 5, wrong_passage 1 |
| argon | retrieve_quote | 12 | 12 | 0 | edition_variant 1, paraphrase 11 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| argon | Hinduism | 100% cov 100% (n=30; c/i/r 30/0/0) | 80% cov 100% (n=30; c/i/r 24/6/0) | 60% cov 100% (n=30; c/i/r 18/12/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **85%** cov 100% (n=120; c/i/r 102/18/0) |

### By text (one text = one work · version · language)

**argon**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 85% | 100% | 0 | — | 17 | 1 | edition_variant 1, paraphrase 16, wrong_passage 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| argon | 120 | 14,393 | 3,394 |
| **total** | 120 | 14,393 | 3,394 |
