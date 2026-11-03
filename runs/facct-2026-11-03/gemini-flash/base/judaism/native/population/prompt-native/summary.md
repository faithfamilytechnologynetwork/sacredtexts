| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemini-flash | 40% cov 100% (n=30; c/i/r 12/18/0; minor/major 0/18) | 10% cov 100% (n=30; c/i/r 3/27/0; minor/major 11/16) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 3/27) | 93% cov 100% (n=30; c/i/r 28/2/0; minor/major 0/2) | **36%** cov 100% (c/i/r 43/77/0; minor/major 14/63) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gemini-flash | cite_passage | 18 | 0 | 18 | wrong_locus 18 |
| gemini-flash | complete_unit | 27 | 11 | 16 | edition_variant 3, paraphrase 6, wrong_passage 16, omission 2 |
| gemini-flash | retrieve_quote | 30 | 3 | 27 | paraphrase 3, wrong_passage 27 |
| gemini-flash | verify_source | 2 | 0 | 2 | wrong_verdict 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemini-flash | Judaism | 40% cov 100% (n=30; c/i/r 12/18/0) | 10% cov 100% (n=30; c/i/r 3/27/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 93% cov 100% (n=30; c/i/r 28/2/0) | **36%** cov 100% (n=120; c/i/r 43/77/0) |

### By text (one text = one work · version · language)

**gemini-flash**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 36% | 100% | 0 | — | 14 | 63 | edition_variant 3, paraphrase 9, wrong_passage 43, omission 2, wrong_locus 18, wrong_verdict 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemini-flash | 120 | 11,569 | 60,542 |
| **total** | 120 | 11,569 | 60,542 |
