| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| astra | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 67% cov 100% (n=30; c/i/r 20/10/0; minor/major 10/0) | 33% cov 100% (n=30; c/i/r 10/20/0; minor/major 20/0) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **75%** cov 100% (c/i/r 90/30/0; minor/major 30/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| astra | complete_unit | 10 | 10 | 0 | edition_variant 4, paraphrase 6 |
| astra | retrieve_quote | 20 | 20 | 0 | edition_variant 2, near_copy 9, paraphrase 9 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| astra | Hinduism | 100% cov 100% (n=30; c/i/r 30/0/0) | 67% cov 100% (n=30; c/i/r 20/10/0) | 33% cov 100% (n=30; c/i/r 10/20/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **75%** cov 100% (n=120; c/i/r 90/30/0) |

### By text (one text = one work · version · language)

**astra**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Annie Besant (1922), en) | 120 | 75% | 100% | 0 | — | 30 | 0 | edition_variant 6, near_copy 9, paraphrase 15 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| astra | 120 | 7,938 | 16,614 |
| **total** | 120 | 7,938 | 16,614 |
