| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| astra | 27% cov 100% (n=30; c/i/r 8/22/0; minor/major 0/22) | 11% cov 93% (n=30; c/i/r 3/25/2; minor/major 7/18) | 0% cov 20% (n=25; c/i/r 0/5/20; minor/major 0/5) | 90% cov 100% (n=30; c/i/r 27/3/0; minor/major 0/3) | **41%** cov 81% (c/i/r 38/55/22; minor/major 7/48) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| astra | cite_passage | 22 | 0 | 22 | wrong_locus 22 |
| astra | complete_unit | 25 | 7 | 18 | diacritic_only 1, edition_variant 2, wrong_passage 18, omission 4 |
| astra | retrieve_quote | 5 | 0 | 5 | wrong_passage 5 |
| astra | verify_source | 3 | 0 | 3 | wrong_verdict 3 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| astra | Sikhism | 27% cov 100% (n=30; c/i/r 8/22/0) | 11% cov 93% (n=30; c/i/r 3/25/2) | 0% cov 20% (n=25; c/i/r 0/5/20) | 90% cov 100% (n=30; c/i/r 27/3/0) | **41%** cov 81% (n=115; c/i/r 38/55/22) |

### By text (one text = one work · version · language)

**astra**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 115 | 41% | 81% | 22 | — | 7 | 48 | diacritic_only 1, edition_variant 2, wrong_passage 23, omission 4, wrong_locus 22, wrong_verdict 3 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| astra | 115 | 12,397 | 54,495 |
| **total** | 115 | 12,397 | 54,495 |
