| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| argon | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 60% cov 100% (n=30; c/i/r 18/12/0; minor/major 12/0) | 24% cov 97% (n=30; c/i/r 7/22/1; minor/major 22/0) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **71%** cov 99% (c/i/r 85/34/1; minor/major 34/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| argon | complete_unit | 12 | 12 | 0 | edition_variant 6, paraphrase 6, addition 2 |
| argon | retrieve_quote | 22 | 22 | 0 | edition_variant 7, near_copy 3, paraphrase 12 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| argon | Hinduism | 100% cov 100% (n=30; c/i/r 30/0/0) | 60% cov 100% (n=30; c/i/r 18/12/0) | 24% cov 97% (n=30; c/i/r 7/22/1) | 100% cov 100% (n=30; c/i/r 30/0/0) | **71%** cov 99% (n=120; c/i/r 85/34/1) |

### By text (one text = one work · version · language)

**argon**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Annie Besant (1922), en) | 120 | 71% | 99% | 1 | — | 34 | 0 | edition_variant 13, near_copy 3, paraphrase 18, addition 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| argon | 120 | 11,058 | 2,372 |
| **total** | 120 | 11,058 | 2,372 |
