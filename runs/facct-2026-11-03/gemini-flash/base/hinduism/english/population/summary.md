| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemini-flash | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 57% cov 100% (n=30; c/i/r 17/13/0; minor/major 12/1) | 23% cov 100% (n=30; c/i/r 7/23/0; minor/major 22/1) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **70%** cov 100% (c/i/r 84/36/0; minor/major 34/2) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gemini-flash | complete_unit | 13 | 12 | 1 | edition_variant 5, near_copy 1, paraphrase 6, wrong_passage 1, addition 1 |
| gemini-flash | retrieve_quote | 23 | 22 | 1 | edition_variant 7, near_copy 4, paraphrase 11, wrong_passage 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemini-flash | Hinduism | 100% cov 100% (n=30; c/i/r 30/0/0) | 57% cov 100% (n=30; c/i/r 17/13/0) | 23% cov 100% (n=30; c/i/r 7/23/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **70%** cov 100% (n=120; c/i/r 84/36/0) |

### By text (one text = one work · version · language)

**gemini-flash**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Annie Besant (1922), en) | 120 | 70% | 100% | 0 | — | 34 | 2 | edition_variant 12, near_copy 5, paraphrase 17, wrong_passage 2, addition 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemini-flash | 120 | 7,355 | 29,728 |
| **total** | 120 | 7,355 | 29,728 |
