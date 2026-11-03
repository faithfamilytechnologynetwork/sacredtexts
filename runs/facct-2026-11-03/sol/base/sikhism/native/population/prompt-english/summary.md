| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sol | 37% cov 100% (n=30; c/i/r 11/19/0; minor/major 0/19) | 7% cov 93% (n=30; c/i/r 2/26/2; minor/major 9/17) | 0% cov 32% (n=25; c/i/r 0/8/17; minor/major 0/8) | 77% cov 100% (n=30; c/i/r 23/7/0; minor/major 0/7) | **38%** cov 83% (c/i/r 36/60/19; minor/major 9/51) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sol | cite_passage | 19 | 0 | 19 | wrong_locus 19 |
| sol | complete_unit | 26 | 9 | 17 | paraphrase 4, wrong_passage 17, omission 5 |
| sol | retrieve_quote | 8 | 0 | 8 | wrong_passage 8 |
| sol | verify_source | 7 | 0 | 7 | wrong_verdict 7 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sol | Sikhism | 37% cov 100% (n=30; c/i/r 11/19/0) | 7% cov 93% (n=30; c/i/r 2/26/2) | 0% cov 32% (n=25; c/i/r 0/8/17) | 77% cov 100% (n=30; c/i/r 23/7/0) | **38%** cov 83% (n=115; c/i/r 36/60/19) |

### By text (one text = one work · version · language)

**sol**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 115 | 38% | 83% | 19 | — | 9 | 51 | paraphrase 4, wrong_passage 25, omission 5, wrong_locus 19, wrong_verdict 7 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sol | 115 | 12,397 | 56,064 |
| **total** | 115 | 12,397 | 56,064 |
