| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| beam | 0% cov 83% (n=30; c/i/r 0/25/5; minor/major 0/25) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 1/29) | 0% cov 8% (n=25; c/i/r 0/2/23; minor/major 0/2) | 80% cov 100% (n=30; c/i/r 24/6/0; minor/major 0/6) | **28%** cov 76% (c/i/r 24/63/28; minor/major 1/62) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| beam | cite_passage | 25 | 0 | 25 | wrong_locus 25 |
| beam | complete_unit | 30 | 1 | 29 | wrong_passage 29, omission 1 |
| beam | retrieve_quote | 2 | 0 | 2 | wrong_passage 2 |
| beam | verify_source | 6 | 0 | 6 | wrong_verdict 6 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| beam | Sikhism | 0% cov 83% (n=30; c/i/r 0/25/5) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 8% (n=25; c/i/r 0/2/23) | 80% cov 100% (n=30; c/i/r 24/6/0) | **28%** cov 76% (n=115; c/i/r 24/63/28) |

### By text (one text = one work · version · language)

**beam**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 115 | 28% | 76% | 28 | — | 1 | 62 | wrong_passage 31, omission 1, wrong_locus 25, wrong_verdict 6 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| beam | 115 | 21,610 | 183,410 |
| **total** | 115 | 21,610 | 183,410 |
