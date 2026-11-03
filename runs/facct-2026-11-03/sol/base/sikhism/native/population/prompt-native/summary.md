| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sol | 20% cov 100% (n=30; c/i/r 6/24/0; minor/major 0/24) | 8% cov 83% (n=30; c/i/r 2/23/5; minor/major 8/15) | 0% cov 4% (n=25; c/i/r 0/1/24; minor/major 0/1) | 93% cov 100% (n=30; c/i/r 28/2/0; minor/major 0/2) | **42%** cov 75% (c/i/r 36/50/29; minor/major 8/42) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sol | cite_passage | 24 | 0 | 24 | wrong_locus 24 |
| sol | complete_unit | 23 | 8 | 15 | paraphrase 3, wrong_passage 15, omission 5 |
| sol | retrieve_quote | 1 | 0 | 1 | wrong_passage 1 |
| sol | verify_source | 2 | 0 | 2 | wrong_verdict 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sol | Sikhism | 20% cov 100% (n=30; c/i/r 6/24/0) | 8% cov 83% (n=30; c/i/r 2/23/5) | 0% cov 4% (n=25; c/i/r 0/1/24) | 93% cov 100% (n=30; c/i/r 28/2/0) | **42%** cov 75% (n=115; c/i/r 36/50/29) |

### By text (one text = one work · version · language)

**sol**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 115 | 42% | 75% | 29 | — | 8 | 42 | paraphrase 3, wrong_passage 16, omission 5, wrong_locus 24, wrong_verdict 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sol | 115 | 10,191 | 43,050 |
| **total** | 115 | 10,191 | 43,050 |
