| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sonnet | 3% cov 100% (n=30; c/i/r 1/29/0; minor/major 0/29) | 14% cov 93% (n=30; c/i/r 4/24/2; minor/major 0/24) | n/a cov 0% (n=30; c/i/r 0/0/30; minor/major 0/0) | 62% cov 27% (n=30; c/i/r 5/3/22; minor/major 0/3) | **15%** cov 55% (c/i/r 10/56/54; minor/major 0/56) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sonnet | cite_passage | 29 | 0 | 29 | hedge 29 |
| sonnet | complete_unit | 24 | 0 | 24 | wrong_passage 9, other_script 15, addition 4 |
| sonnet | verify_source | 3 | 0 | 3 | wrong_verdict 3 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sonnet | Judaism | 3% cov 100% (n=30; c/i/r 1/29/0) | 14% cov 93% (n=30; c/i/r 4/24/2) | n/a cov 0% (n=30; c/i/r 0/0/30) | 62% cov 27% (n=30; c/i/r 5/3/22) | **15%** cov 55% (n=120; c/i/r 10/56/54) |

### By text (one text = one work · version · language)

**sonnet**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 15% | 55% | 54 | — | 0 | 56 | wrong_passage 9, other_script 15, addition 4, hedge 29, wrong_verdict 3 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sonnet | 120 | 17,875 | 43,703 |
| **total** | 120 | 17,875 | 43,703 |
