| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemini-flash | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 73% cov 100% (n=30; c/i/r 22/8/0; minor/major 6/2) | 53% cov 100% (n=30; c/i/r 16/14/0; minor/major 14/0) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **82%** cov 100% (c/i/r 98/22/0; minor/major 20/2) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gemini-flash | complete_unit | 8 | 6 | 2 | edition_variant 1, paraphrase 5, wrong_passage 2 |
| gemini-flash | retrieve_quote | 14 | 14 | 0 | diacritic_only 1, edition_variant 5, paraphrase 8 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemini-flash | Hinduism | 100% cov 100% (n=30; c/i/r 30/0/0) | 73% cov 100% (n=30; c/i/r 22/8/0) | 53% cov 100% (n=30; c/i/r 16/14/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **82%** cov 100% (n=120; c/i/r 98/22/0) |

### By text (one text = one work · version · language)

**gemini-flash**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 82% | 100% | 0 | — | 20 | 2 | diacritic_only 1, edition_variant 6, paraphrase 13, wrong_passage 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemini-flash | 120 | 10,382 | 11,910 |
| **total** | 120 | 10,382 | 11,910 |
