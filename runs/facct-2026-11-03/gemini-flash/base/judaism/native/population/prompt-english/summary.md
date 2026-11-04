| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemini-flash | 27% cov 100% (n=30; c/i/r 8/22/0; minor/major 0/22) | 17% cov 100% (n=30; c/i/r 5/25/0; minor/major 12/13) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 2/28) | 83% cov 100% (n=30; c/i/r 25/5/0; minor/major 0/5) | **32%** cov 100% (c/i/r 38/82/0; minor/major 14/68) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gemini-flash | cite_passage | 22 | 0 | 22 | wrong_locus 22 |
| gemini-flash | complete_unit | 25 | 12 | 13 | edition_variant 2, near_copy 1, paraphrase 6, wrong_passage 13, omission 3 |
| gemini-flash | retrieve_quote | 30 | 2 | 28 | paraphrase 2, wrong_passage 28 |
| gemini-flash | verify_source | 5 | 0 | 5 | wrong_verdict 5 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemini-flash | Judaism | 27% cov 100% (n=30; c/i/r 8/22/0) | 17% cov 100% (n=30; c/i/r 5/25/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 83% cov 100% (n=30; c/i/r 25/5/0) | **32%** cov 100% (n=120; c/i/r 38/82/0) |

### By text (one text = one work · version · language)

**gemini-flash**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 32% | 100% | 0 | — | 14 | 68 | edition_variant 2, near_copy 1, paraphrase 8, wrong_passage 41, omission 3, wrong_locus 22, wrong_verdict 5 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemini-flash | 120 | 11,198 | 82,376 |
| **total** | 120 | 11,198 | 82,376 |
