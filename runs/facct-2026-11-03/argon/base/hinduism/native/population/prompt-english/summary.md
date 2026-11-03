| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| argon | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 70% cov 100% (n=30; c/i/r 21/9/0; minor/major 8/1) | 50% cov 100% (n=30; c/i/r 15/15/0; minor/major 15/0) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **80%** cov 100% (c/i/r 96/24/0; minor/major 23/1) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| argon | complete_unit | 9 | 8 | 1 | edition_variant 2, paraphrase 6, wrong_passage 1 |
| argon | retrieve_quote | 15 | 15 | 0 | edition_variant 4, paraphrase 11 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| argon | Hinduism | 100% cov 100% (n=30; c/i/r 30/0/0) | 70% cov 100% (n=30; c/i/r 21/9/0) | 50% cov 100% (n=30; c/i/r 15/15/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **80%** cov 100% (n=120; c/i/r 96/24/0) |

### By text (one text = one work · version · language)

**argon**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 80% | 100% | 0 | — | 23 | 1 | edition_variant 6, paraphrase 17, wrong_passage 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| argon | 120 | 14,393 | 3,394 |
| **total** | 120 | 14,393 | 3,394 |
