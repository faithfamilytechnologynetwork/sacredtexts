| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| argon | 13% cov 100% (n=30; c/i/r 4/26/0; minor/major 0/26) | 3% cov 100% (n=30; c/i/r 1/29/0; minor/major 13/16) | 0% cov 88% (n=25; c/i/r 0/22/3; minor/major 0/22) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **31%** cov 97% (c/i/r 35/77/3; minor/major 13/64) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| argon | cite_passage | 26 | 0 | 26 | wrong_locus 26 |
| argon | complete_unit | 29 | 13 | 16 | edition_variant 4, paraphrase 7, wrong_passage 16, omission 2 |
| argon | retrieve_quote | 22 | 0 | 22 | wrong_passage 22 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| argon | Sikhism | 13% cov 100% (n=30; c/i/r 4/26/0) | 3% cov 100% (n=30; c/i/r 1/29/0) | 0% cov 88% (n=25; c/i/r 0/22/3) | 100% cov 100% (n=30; c/i/r 30/0/0) | **31%** cov 97% (n=115; c/i/r 35/77/3) |

### By text (one text = one work · version · language)

**argon**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 115 | 31% | 97% | 3 | — | 13 | 64 | edition_variant 4, paraphrase 7, wrong_passage 38, omission 2, wrong_locus 26 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| argon | 115 | 15,099 | 3,222 |
| **total** | 115 | 15,099 | 3,222 |
