| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| astra | 60% cov 100% (n=30; c/i/r 18/12/0; minor/major 0/12) | 43% cov 100% (n=30; c/i/r 13/17/0; minor/major 11/6) | 19% cov 70% (n=30; c/i/r 4/17/9; minor/major 2/15) | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | **58%** cov 92% (c/i/r 64/47/9; minor/major 13/34) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| astra | cite_passage | 12 | 0 | 12 | wrong_locus 12 |
| astra | complete_unit | 17 | 11 | 6 | edition_variant 3, paraphrase 5, wrong_passage 6, omission 3, addition 2 |
| astra | retrieve_quote | 17 | 2 | 15 | paraphrase 2, wrong_passage 15, addition 2 |
| astra | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| astra | Judaism | 60% cov 100% (n=30; c/i/r 18/12/0) | 43% cov 100% (n=30; c/i/r 13/17/0) | 19% cov 70% (n=30; c/i/r 4/17/9) | 97% cov 100% (n=30; c/i/r 29/1/0) | **58%** cov 92% (n=120; c/i/r 64/47/9) |

### By text (one text = one work · version · language)

**astra**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 58% | 92% | 9 | — | 13 | 34 | edition_variant 3, paraphrase 7, wrong_passage 21, omission 3, addition 4, wrong_locus 12, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| astra | 120 | 11,948 | 47,703 |
| **total** | 120 | 11,948 | 47,703 |
