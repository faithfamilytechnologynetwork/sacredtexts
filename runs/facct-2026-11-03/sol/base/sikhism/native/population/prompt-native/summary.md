| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sol | 30% cov 100% (n=30; c/i/r 9/21/0; minor/major 0/21) | 8% cov 83% (n=30; c/i/r 2/23/5; minor/major 8/15) | 0% cov 27% (n=30; c/i/r 0/8/22; minor/major 0/8) | 93% cov 100% (n=30; c/i/r 28/2/0; minor/major 0/2) | **42%** cov 78% (c/i/r 39/54/27; minor/major 8/46) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sol | cite_passage | 21 | 0 | 21 | wrong_locus 21 |
| sol | complete_unit | 23 | 8 | 15 | paraphrase 3, wrong_passage 15, omission 5 |
| sol | retrieve_quote | 8 | 0 | 8 | wrong_passage 8 |
| sol | verify_source | 2 | 0 | 2 | wrong_verdict 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sol | Sikhism | 30% cov 100% (n=30; c/i/r 9/21/0) | 8% cov 83% (n=30; c/i/r 2/23/5) | 0% cov 27% (n=30; c/i/r 0/8/22) | 93% cov 100% (n=30; c/i/r 28/2/0) | **42%** cov 78% (n=120; c/i/r 39/54/27) |

### By text (one text = one work · version · language)

**sol**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 120 | 42% | 78% | 27 | — | 8 | 46 | paraphrase 3, wrong_passage 23, omission 5, wrong_locus 21, wrong_verdict 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sol | 120 | 10,290 | 45,945 |
| **total** | 120 | 10,290 | 45,945 |
