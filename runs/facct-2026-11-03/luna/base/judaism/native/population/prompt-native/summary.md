| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| luna | 20% cov 100% (n=30; c/i/r 6/24/0; minor/major 0/24) | 3% cov 100% (n=30; c/i/r 1/29/0; minor/major 6/23) | 0% cov 67% (n=30; c/i/r 0/20/10; minor/major 0/20) | 67% cov 100% (n=30; c/i/r 20/10/0; minor/major 0/10) | **25%** cov 92% (c/i/r 27/83/10; minor/major 6/77) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| luna | cite_passage | 24 | 0 | 24 | wrong_locus 24 |
| luna | complete_unit | 29 | 6 | 23 | edition_variant 1, paraphrase 4, wrong_passage 23, omission 1, addition 1 |
| luna | retrieve_quote | 20 | 0 | 20 | wrong_passage 20 |
| luna | verify_source | 10 | 0 | 10 | wrong_verdict 10 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| luna | Judaism | 20% cov 100% (n=30; c/i/r 6/24/0) | 3% cov 100% (n=30; c/i/r 1/29/0) | 0% cov 67% (n=30; c/i/r 0/20/10) | 67% cov 100% (n=30; c/i/r 20/10/0) | **25%** cov 92% (n=120; c/i/r 27/83/10) |

### By text (one text = one work · version · language)

**luna**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 25% | 92% | 10 | — | 6 | 77 | edition_variant 1, paraphrase 4, wrong_passage 43, omission 1, addition 1, wrong_locus 24, wrong_verdict 10 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| luna | 120 | 11,478 | 6,602 |
| **total** | 120 | 11,478 | 6,602 |
