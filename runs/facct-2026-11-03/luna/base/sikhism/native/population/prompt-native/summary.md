| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| luna | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 1/29) | 0% cov 87% (n=30; c/i/r 0/26/4; minor/major 0/26) | 93% cov 100% (n=30; c/i/r 28/2/0; minor/major 0/2) | **24%** cov 97% (c/i/r 28/88/4; minor/major 1/87) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| luna | cite_passage | 30 | 0 | 30 | wrong_locus 30 |
| luna | complete_unit | 30 | 1 | 29 | wrong_passage 29, omission 1 |
| luna | retrieve_quote | 26 | 0 | 26 | wrong_passage 26 |
| luna | verify_source | 2 | 0 | 2 | wrong_verdict 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| luna | Sikhism | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 87% (n=30; c/i/r 0/26/4) | 93% cov 100% (n=30; c/i/r 28/2/0) | **24%** cov 97% (n=120; c/i/r 28/88/4) |

### By text (one text = one work · version · language)

**luna**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 120 | 24% | 97% | 4 | — | 1 | 87 | wrong_passage 55, omission 1, wrong_locus 30, wrong_verdict 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| luna | 120 | 10,290 | 6,403 |
| **total** | 120 | 10,290 | 6,403 |
