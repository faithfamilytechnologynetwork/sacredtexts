| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| opus | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 73% cov 100% (n=30; c/i/r 22/8/0; minor/major 6/2) | 61% cov 77% (n=30; c/i/r 14/9/7; minor/major 9/0) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **85%** cov 94% (c/i/r 96/17/7; minor/major 15/2) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| opus | complete_unit | 8 | 6 | 2 | edition_variant 3, paraphrase 3, wrong_passage 2, addition 2 |
| opus | retrieve_quote | 9 | 9 | 0 | paraphrase 9, addition 7 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| opus | Hinduism | 100% cov 100% (n=30; c/i/r 30/0/0) | 73% cov 100% (n=30; c/i/r 22/8/0) | 61% cov 77% (n=30; c/i/r 14/9/7) | 100% cov 100% (n=30; c/i/r 30/0/0) | **85%** cov 94% (n=120; c/i/r 96/17/7) |

### By text (one text = one work · version · language)

**opus**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Annie Besant (1922), en) | 120 | 85% | 94% | 7 | — | 15 | 2 | edition_variant 3, paraphrase 12, wrong_passage 2, addition 9 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| opus | 120 | 11,579 | 29,038 |
| **total** | 120 | 11,579 | 29,038 |
