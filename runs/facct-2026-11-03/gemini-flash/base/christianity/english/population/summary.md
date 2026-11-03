| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemini-flash | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 71% cov 57% (n=30; c/i/r 12/5/13; minor/major 5/0) | 79% cov 97% (n=30; c/i/r 23/6/1; minor/major 6/0) | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | **89%** cov 88% (c/i/r 94/12/14; minor/major 11/1) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gemini-flash | complete_unit | 5 | 5 | 0 | edition_variant 2, near_copy 1, paraphrase 1, omission 1 |
| gemini-flash | retrieve_quote | 6 | 6 | 0 | edition_variant 1, near_copy 5 |
| gemini-flash | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemini-flash | Christianity | 100% cov 100% (n=30; c/i/r 30/0/0) | 71% cov 57% (n=30; c/i/r 12/5/13) | 79% cov 97% (n=30; c/i/r 23/6/1) | 97% cov 100% (n=30; c/i/r 29/1/0) | **89%** cov 88% (n=120; c/i/r 94/12/14) |

### By text (one text = one work · version · language)

**gemini-flash**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (NRSV, en) | 120 | 89% | 88% | 14 | — | 11 | 1 | edition_variant 3, near_copy 6, paraphrase 1, omission 1, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemini-flash | 120 | 6,186 | 12,425 |
| **total** | 120 | 6,186 | 12,425 |
