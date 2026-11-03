| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| beam | 0% cov 77% (n=30; c/i/r 0/23/7; minor/major 0/23) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 1/29) | n/a cov 0% (n=30; c/i/r 0/0/30; minor/major 0/0) | 80% cov 100% (n=30; c/i/r 24/6/0; minor/major 0/6) | **29%** cov 69% (c/i/r 24/59/37; minor/major 1/58) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| beam | cite_passage | 23 | 0 | 23 | wrong_locus 21, no_citation 2 |
| beam | complete_unit | 30 | 1 | 29 | wrong_passage 29, omission 1 |
| beam | verify_source | 6 | 0 | 6 | wrong_verdict 6 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| beam | Sikhism | 0% cov 77% (n=30; c/i/r 0/23/7) | 0% cov 100% (n=30; c/i/r 0/30/0) | n/a cov 0% (n=30; c/i/r 0/0/30) | 80% cov 100% (n=30; c/i/r 24/6/0) | **29%** cov 69% (n=120; c/i/r 24/59/37) |

### By text (one text = one work · version · language)

**beam**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 120 | 29% | 69% | 37 | — | 1 | 58 | wrong_passage 29, omission 1, wrong_locus 21, no_citation 2, wrong_verdict 6 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| beam | 120 | 22,209 | 182,172 |
| **total** | 120 | 22,209 | 182,172 |
