| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| argon | 13% cov 100% (n=30; c/i/r 4/26/0; minor/major 0/26) | 3% cov 100% (n=30; c/i/r 1/29/0; minor/major 14/15) | 0% cov 24% (n=25; c/i/r 0/6/19; minor/major 0/6) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **36%** cov 83% (c/i/r 35/61/19; minor/major 14/47) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| argon | cite_passage | 26 | 0 | 26 | wrong_locus 26 |
| argon | complete_unit | 29 | 14 | 15 | edition_variant 4, near_copy 1, paraphrase 5, wrong_passage 15, omission 4 |
| argon | retrieve_quote | 6 | 0 | 6 | wrong_passage 6 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| argon | Sikhism | 13% cov 100% (n=30; c/i/r 4/26/0) | 3% cov 100% (n=30; c/i/r 1/29/0) | 0% cov 24% (n=25; c/i/r 0/6/19) | 100% cov 100% (n=30; c/i/r 30/0/0) | **36%** cov 83% (n=115; c/i/r 35/61/19) |

### By text (one text = one work · version · language)

**argon**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 115 | 36% | 83% | 19 | — | 14 | 47 | edition_variant 4, near_copy 1, paraphrase 5, wrong_passage 21, omission 4, wrong_locus 26 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| argon | 115 | 12,211 | 7,002 |
| **total** | 115 | 12,211 | 7,002 |
