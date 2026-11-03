| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| haiku | 0% cov 50% (n=30; c/i/r 0/15/15; minor/major 0/15) | 0% cov 83% (n=30; c/i/r 0/25/5; minor/major 0/25) | 0% cov 50% (n=30; c/i/r 0/15/15; minor/major 0/15) | 97% cov 97% (n=30; c/i/r 28/1/1; minor/major 0/1) | **33%** cov 70% (c/i/r 28/56/36; minor/major 0/56) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| haiku | cite_passage | 15 | 0 | 15 | wrong_locus 15 |
| haiku | complete_unit | 25 | 0 | 25 | wrong_passage 25 |
| haiku | retrieve_quote | 15 | 0 | 15 | wrong_passage 15 |
| haiku | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| haiku | Sikhism | 0% cov 50% (n=30; c/i/r 0/15/15) | 0% cov 83% (n=30; c/i/r 0/25/5) | 0% cov 50% (n=30; c/i/r 0/15/15) | 97% cov 97% (n=30; c/i/r 28/1/1) | **33%** cov 70% (n=120; c/i/r 28/56/36) |

### By text (one text = one work · version · language)

**haiku**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 120 | 33% | 70% | 36 | — | 0 | 56 | wrong_passage 40, wrong_locus 15, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| haiku | 120 | 30,178 | 87,015 |
| **total** | 120 | 30,178 | 87,015 |
