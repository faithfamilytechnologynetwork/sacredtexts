| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sonnet | 14% cov 70% (n=30; c/i/r 3/18/9; minor/major 0/18) | 0% cov 70% (n=30; c/i/r 0/21/9; minor/major 1/20) | 0% cov 10% (n=30; c/i/r 0/3/27; minor/major 0/3) | 50% cov 100% (n=30; c/i/r 15/15/0; minor/major 0/15) | **24%** cov 62% (c/i/r 18/57/45; minor/major 1/56) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sonnet | cite_passage | 18 | 0 | 18 | wrong_locus 15, hedge 3 |
| sonnet | complete_unit | 21 | 1 | 20 | edition_variant 1, wrong_passage 20 |
| sonnet | retrieve_quote | 3 | 0 | 3 | wrong_passage 3 |
| sonnet | verify_source | 15 | 0 | 15 | wrong_verdict 15 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sonnet | Judaism | 14% cov 70% (n=30; c/i/r 3/18/9) | 0% cov 70% (n=30; c/i/r 0/21/9) | 0% cov 10% (n=30; c/i/r 0/3/27) | 50% cov 100% (n=30; c/i/r 15/15/0) | **24%** cov 62% (n=120; c/i/r 18/57/45) |

### By text (one text = one work · version · language)

**sonnet**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 24% | 62% | 45 | — | 1 | 56 | edition_variant 1, wrong_passage 23, wrong_locus 15, hedge 3, wrong_verdict 15 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sonnet | 120 | 17,877 | 47,286 |
| **total** | 120 | 17,877 | 47,286 |
