| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemini-flash | 10% cov 100% (n=30; c/i/r 3/27/0; minor/major 0/27) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 4/26) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 77% cov 100% (n=30; c/i/r 23/7/0; minor/major 0/7) | **22%** cov 100% (c/i/r 26/94/0; minor/major 4/90) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gemini-flash | cite_passage | 27 | 0 | 27 | wrong_locus 27 |
| gemini-flash | complete_unit | 30 | 4 | 26 | paraphrase 3, wrong_passage 26, omission 1 |
| gemini-flash | retrieve_quote | 30 | 0 | 30 | wrong_passage 30 |
| gemini-flash | verify_source | 7 | 0 | 7 | wrong_verdict 7 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemini-flash | Sikhism | 10% cov 100% (n=30; c/i/r 3/27/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 77% cov 100% (n=30; c/i/r 23/7/0) | **22%** cov 100% (n=120; c/i/r 26/94/0) |

### By text (one text = one work · version · language)

**gemini-flash**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 120 | 22% | 100% | 0 | — | 4 | 90 | paraphrase 3, wrong_passage 56, omission 1, wrong_locus 27, wrong_verdict 7 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemini-flash | 120 | 12,211 | 75,663 |
| **total** | 120 | 12,211 | 75,663 |
