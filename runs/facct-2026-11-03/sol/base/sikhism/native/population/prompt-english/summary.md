| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sol | 33% cov 100% (n=30; c/i/r 10/20/0; minor/major 0/20) | 7% cov 93% (n=30; c/i/r 2/26/2; minor/major 9/17) | 0% cov 10% (n=30; c/i/r 0/3/27; minor/major 0/3) | 77% cov 100% (n=30; c/i/r 23/7/0; minor/major 0/7) | **38%** cov 76% (c/i/r 35/56/29; minor/major 9/47) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sol | cite_passage | 20 | 0 | 20 | wrong_locus 20 |
| sol | complete_unit | 26 | 9 | 17 | paraphrase 4, wrong_passage 17, omission 5 |
| sol | retrieve_quote | 3 | 0 | 3 | wrong_passage 3 |
| sol | verify_source | 7 | 0 | 7 | wrong_verdict 7 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sol | Sikhism | 33% cov 100% (n=30; c/i/r 10/20/0) | 7% cov 93% (n=30; c/i/r 2/26/2) | 0% cov 10% (n=30; c/i/r 0/3/27) | 77% cov 100% (n=30; c/i/r 23/7/0) | **38%** cov 76% (n=120; c/i/r 35/56/29) |

### By text (one text = one work · version · language)

**sol**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 120 | 38% | 76% | 29 | — | 9 | 47 | paraphrase 4, wrong_passage 20, omission 5, wrong_locus 20, wrong_verdict 7 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sol | 120 | 12,749 | 55,691 |
| **total** | 120 | 12,749 | 55,691 |
