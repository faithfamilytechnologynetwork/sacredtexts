| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemini-flash | 37% cov 100% (n=30; c/i/r 11/19/0; minor/major 0/19) | 23% cov 100% (n=30; c/i/r 7/23/0; minor/major 9/14) | 3% cov 100% (n=30; c/i/r 1/29/0; minor/major 2/27) | 73% cov 100% (n=30; c/i/r 22/8/0; minor/major 0/8) | **34%** cov 100% (c/i/r 41/79/0; minor/major 11/68) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gemini-flash | cite_passage | 19 | 0 | 19 | wrong_locus 19 |
| gemini-flash | complete_unit | 23 | 9 | 14 | edition_variant 1, paraphrase 6, wrong_passage 14, omission 2 |
| gemini-flash | retrieve_quote | 29 | 2 | 27 | paraphrase 2, wrong_passage 27, addition 1 |
| gemini-flash | verify_source | 8 | 0 | 8 | wrong_verdict 8 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemini-flash | Judaism | 37% cov 100% (n=30; c/i/r 11/19/0) | 23% cov 100% (n=30; c/i/r 7/23/0) | 3% cov 100% (n=30; c/i/r 1/29/0) | 73% cov 100% (n=30; c/i/r 22/8/0) | **34%** cov 100% (n=120; c/i/r 41/79/0) |

### By text (one text = one work · version · language)

**gemini-flash**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 34% | 100% | 0 | — | 11 | 68 | edition_variant 1, paraphrase 8, wrong_passage 41, omission 2, addition 1, wrong_locus 19, wrong_verdict 8 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemini-flash | 120 | 10,607 | 52,132 |
| **total** | 120 | 10,607 | 52,132 |
