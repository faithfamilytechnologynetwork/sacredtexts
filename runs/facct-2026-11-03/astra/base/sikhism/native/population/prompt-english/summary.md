| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| astra | 37% cov 100% (n=30; c/i/r 11/19/0; minor/major 0/19) | 11% cov 93% (n=30; c/i/r 3/25/2; minor/major 7/18) | 0% cov 10% (n=30; c/i/r 0/3/27; minor/major 0/3) | 90% cov 100% (n=30; c/i/r 27/3/0; minor/major 0/3) | **45%** cov 76% (c/i/r 41/50/29; minor/major 7/43) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| astra | cite_passage | 19 | 0 | 19 | wrong_locus 19 |
| astra | complete_unit | 25 | 7 | 18 | diacritic_only 1, edition_variant 2, wrong_passage 18, omission 4 |
| astra | retrieve_quote | 3 | 0 | 3 | wrong_passage 3 |
| astra | verify_source | 3 | 0 | 3 | wrong_verdict 3 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| astra | Sikhism | 37% cov 100% (n=30; c/i/r 11/19/0) | 11% cov 93% (n=30; c/i/r 3/25/2) | 0% cov 10% (n=30; c/i/r 0/3/27) | 90% cov 100% (n=30; c/i/r 27/3/0) | **45%** cov 76% (n=120; c/i/r 41/50/29) |

### By text (one text = one work · version · language)

**astra**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 120 | 45% | 76% | 29 | — | 7 | 43 | diacritic_only 1, edition_variant 2, wrong_passage 21, omission 4, wrong_locus 19, wrong_verdict 3 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| astra | 120 | 12,749 | 55,874 |
| **total** | 120 | 12,749 | 55,874 |
