| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| terra | 53% cov 100% (n=30; c/i/r 16/14/0; minor/major 0/14) | 20% cov 100% (n=30; c/i/r 6/24/0; minor/major 11/13) | 7% cov 100% (n=30; c/i/r 2/28/0; minor/major 1/27) | 80% cov 100% (n=30; c/i/r 24/6/0; minor/major 0/6) | **40%** cov 100% (c/i/r 48/72/0; minor/major 12/60) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| terra | cite_passage | 14 | 0 | 14 | wrong_locus 14 |
| terra | complete_unit | 24 | 11 | 13 | edition_variant 2, paraphrase 6, wrong_passage 13, omission 3 |
| terra | retrieve_quote | 28 | 1 | 27 | edition_variant 1, wrong_passage 27, addition 1 |
| terra | verify_source | 6 | 0 | 6 | wrong_verdict 6 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| terra | Judaism | 53% cov 100% (n=30; c/i/r 16/14/0) | 20% cov 100% (n=30; c/i/r 6/24/0) | 7% cov 100% (n=30; c/i/r 2/28/0) | 80% cov 100% (n=30; c/i/r 24/6/0) | **40%** cov 100% (n=120; c/i/r 48/72/0) |

### By text (one text = one work · version · language)

**terra**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 40% | 100% | 0 | — | 12 | 60 | edition_variant 3, paraphrase 6, wrong_passage 40, omission 3, addition 1, wrong_locus 14, wrong_verdict 6 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| terra | 120 | 11,948 | 10,604 |
| **total** | 120 | 11,948 | 10,604 |
