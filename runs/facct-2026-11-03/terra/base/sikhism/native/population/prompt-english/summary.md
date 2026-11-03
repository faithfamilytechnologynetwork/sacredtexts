| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| terra | 13% cov 100% (n=30; c/i/r 4/26/0; minor/major 0/26) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 1/29) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 83% cov 100% (n=30; c/i/r 25/5/0; minor/major 0/5) | **24%** cov 100% (c/i/r 29/91/0; minor/major 1/90) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| terra | cite_passage | 26 | 0 | 26 | wrong_locus 26 |
| terra | complete_unit | 30 | 1 | 29 | diacritic_only 1, wrong_passage 29 |
| terra | retrieve_quote | 30 | 0 | 30 | wrong_passage 30 |
| terra | verify_source | 5 | 0 | 5 | wrong_verdict 5 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| terra | Sikhism | 13% cov 100% (n=30; c/i/r 4/26/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 83% cov 100% (n=30; c/i/r 25/5/0) | **24%** cov 100% (n=120; c/i/r 29/91/0) |

### By text (one text = one work · version · language)

**terra**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 120 | 24% | 100% | 0 | — | 1 | 90 | diacritic_only 1, wrong_passage 59, wrong_locus 26, wrong_verdict 5 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| terra | 120 | 12,749 | 2,293 |
| **total** | 120 | 12,749 | 2,293 |
