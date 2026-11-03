| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| argon | 20% cov 100% (n=30; c/i/r 6/24/0; minor/major 0/24) | 3% cov 100% (n=30; c/i/r 1/29/0; minor/major 13/16) | 0% cov 70% (n=30; c/i/r 0/21/9; minor/major 0/21) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **33%** cov 92% (c/i/r 37/74/9; minor/major 13/61) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| argon | cite_passage | 24 | 0 | 24 | wrong_locus 24 |
| argon | complete_unit | 29 | 13 | 16 | edition_variant 4, paraphrase 7, wrong_passage 16, omission 2 |
| argon | retrieve_quote | 21 | 0 | 21 | wrong_passage 21 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| argon | Sikhism | 20% cov 100% (n=30; c/i/r 6/24/0) | 3% cov 100% (n=30; c/i/r 1/29/0) | 0% cov 70% (n=30; c/i/r 0/21/9) | 100% cov 100% (n=30; c/i/r 30/0/0) | **33%** cov 92% (n=120; c/i/r 37/74/9) |

### By text (one text = one work · version · language)

**argon**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 120 | 33% | 92% | 9 | — | 13 | 61 | edition_variant 4, paraphrase 7, wrong_passage 37, omission 2, wrong_locus 24 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| argon | 120 | 15,610 | 4,714 |
| **total** | 120 | 15,610 | 4,714 |
