| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sonnet | 4% cov 83% (n=30; c/i/r 1/24/5; minor/major 0/24) | 0% cov 33% (n=30; c/i/r 0/10/20; minor/major 0/10) | n/a cov 0% (n=30; c/i/r 0/0/30; minor/major 0/0) | 96% cov 77% (n=30; c/i/r 22/1/7; minor/major 0/1) | **40%** cov 48% (c/i/r 23/35/62; minor/major 0/35) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sonnet | cite_passage | 24 | 0 | 24 | hedge 24 |
| sonnet | complete_unit | 10 | 0 | 10 | wrong_passage 10 |
| sonnet | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sonnet | Judaism | 4% cov 83% (n=30; c/i/r 1/24/5) | 0% cov 33% (n=30; c/i/r 0/10/20) | n/a cov 0% (n=30; c/i/r 0/0/30) | 96% cov 77% (n=30; c/i/r 22/1/7) | **40%** cov 48% (n=120; c/i/r 23/35/62) |

### By text (one text = one work · version · language)

**sonnet**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - English, en) | 120 | 40% | 48% | 62 | — | 0 | 35 | wrong_passage 10, hedge 24, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sonnet | 120 | 18,967 | 33,199 |
| **total** | 120 | 18,967 | 33,199 |
