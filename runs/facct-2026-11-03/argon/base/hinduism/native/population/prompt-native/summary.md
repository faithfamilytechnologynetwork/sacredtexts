| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| argon | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 70% cov 100% (n=30; c/i/r 21/9/0; minor/major 6/3) | 63% cov 100% (n=30; c/i/r 19/11/0; minor/major 9/2) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **83%** cov 100% (c/i/r 100/20/0; minor/major 15/5) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| argon | complete_unit | 9 | 6 | 3 | paraphrase 6, wrong_passage 3 |
| argon | retrieve_quote | 11 | 9 | 2 | paraphrase 9, wrong_passage 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| argon | Hinduism | 100% cov 100% (n=30; c/i/r 30/0/0) | 70% cov 100% (n=30; c/i/r 21/9/0) | 63% cov 100% (n=30; c/i/r 19/11/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **83%** cov 100% (n=120; c/i/r 100/20/0) |

### By text (one text = one work · version · language)

**argon**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 83% | 100% | 0 | — | 15 | 5 | paraphrase 15, wrong_passage 5 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| argon | 120 | 12,208 | 2,947 |
| **total** | 120 | 12,208 | 2,947 |
