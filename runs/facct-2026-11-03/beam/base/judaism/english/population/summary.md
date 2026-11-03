| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| beam | 23% cov 100% (n=30; c/i/r 7/23/0; minor/major 0/23) | 0% cov 97% (n=30; c/i/r 0/29/1; minor/major 8/21) | 0% cov 3% (n=30; c/i/r 0/1/29; minor/major 0/1) | 83% cov 100% (n=30; c/i/r 25/5/0; minor/major 0/5) | **36%** cov 75% (c/i/r 32/58/30; minor/major 8/50) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| beam | cite_passage | 23 | 0 | 23 | wrong_locus 23 |
| beam | complete_unit | 29 | 8 | 21 | paraphrase 5, wrong_passage 21, omission 3 |
| beam | retrieve_quote | 1 | 0 | 1 | wrong_passage 1 |
| beam | verify_source | 5 | 0 | 5 | wrong_verdict 5 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| beam | Judaism | 23% cov 100% (n=30; c/i/r 7/23/0) | 0% cov 97% (n=30; c/i/r 0/29/1) | 0% cov 3% (n=30; c/i/r 0/1/29) | 83% cov 100% (n=30; c/i/r 25/5/0) | **36%** cov 75% (n=120; c/i/r 32/58/30) |

### By text (one text = one work · version · language)

**beam**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - English, en) | 120 | 36% | 75% | 30 | — | 8 | 50 | paraphrase 5, wrong_passage 22, omission 3, wrong_locus 23, wrong_verdict 5 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| beam | 120 | 18,017 | 143,387 |
| **total** | 120 | 18,017 | 143,387 |
