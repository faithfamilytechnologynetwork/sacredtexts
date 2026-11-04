| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| terra | 43% cov 100% (n=30; c/i/r 13/17/0; minor/major 0/17) | 17% cov 100% (n=30; c/i/r 5/25/0; minor/major 12/13) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 1/29) | 67% cov 100% (n=30; c/i/r 20/10/0; minor/major 0/10) | **32%** cov 100% (c/i/r 38/82/0; minor/major 13/69) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| terra | cite_passage | 17 | 0 | 17 | wrong_locus 17 |
| terra | complete_unit | 25 | 12 | 13 | edition_variant 1, paraphrase 8, wrong_passage 13, omission 3 |
| terra | retrieve_quote | 30 | 1 | 29 | paraphrase 1, wrong_passage 29 |
| terra | verify_source | 10 | 0 | 10 | wrong_verdict 10 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| terra | Judaism | 43% cov 100% (n=30; c/i/r 13/17/0) | 17% cov 100% (n=30; c/i/r 5/25/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 67% cov 100% (n=30; c/i/r 20/10/0) | **32%** cov 100% (n=120; c/i/r 38/82/0) |

### By text (one text = one work · version · language)

**terra**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 32% | 100% | 0 | — | 13 | 69 | edition_variant 1, paraphrase 9, wrong_passage 42, omission 3, wrong_locus 17, wrong_verdict 10 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| terra | 120 | 10,488 | 8,640 |
| **total** | 120 | 10,488 | 8,640 |
