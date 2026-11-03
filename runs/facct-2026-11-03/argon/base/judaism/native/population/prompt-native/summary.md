| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| argon | 37% cov 100% (n=30; c/i/r 11/19/0; minor/major 0/19) | 13% cov 100% (n=30; c/i/r 4/26/0; minor/major 13/13) | 0% cov 50% (n=30; c/i/r 0/15/15; minor/major 1/14) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **43%** cov 88% (c/i/r 45/60/15; minor/major 14/46) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| argon | cite_passage | 19 | 0 | 19 | wrong_locus 19 |
| argon | complete_unit | 26 | 13 | 13 | edition_variant 4, near_copy 1, paraphrase 6, wrong_passage 13, omission 2 |
| argon | retrieve_quote | 15 | 1 | 14 | paraphrase 1, wrong_passage 14 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| argon | Judaism | 37% cov 100% (n=30; c/i/r 11/19/0) | 13% cov 100% (n=30; c/i/r 4/26/0) | 0% cov 50% (n=30; c/i/r 0/15/15) | 100% cov 100% (n=30; c/i/r 30/0/0) | **43%** cov 88% (n=120; c/i/r 45/60/15) |

### By text (one text = one work · version · language)

**argon**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 43% | 88% | 15 | — | 14 | 46 | edition_variant 4, near_copy 1, paraphrase 7, wrong_passage 27, omission 2, wrong_locus 19 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| argon | 120 | 23,474 | 12,200 |
| **total** | 120 | 23,474 | 12,200 |
