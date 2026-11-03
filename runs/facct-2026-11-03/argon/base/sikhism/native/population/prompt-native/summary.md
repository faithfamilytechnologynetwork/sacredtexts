| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| argon | 17% cov 100% (n=30; c/i/r 5/25/0; minor/major 0/25) | 3% cov 100% (n=30; c/i/r 1/29/0; minor/major 14/15) | 0% cov 73% (n=30; c/i/r 0/22/8; minor/major 0/22) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **32%** cov 93% (c/i/r 36/76/8; minor/major 14/62) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| argon | cite_passage | 25 | 0 | 25 | wrong_locus 25 |
| argon | complete_unit | 29 | 14 | 15 | edition_variant 4, near_copy 1, paraphrase 5, wrong_passage 15, omission 4 |
| argon | retrieve_quote | 22 | 0 | 22 | wrong_passage 22 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| argon | Sikhism | 17% cov 100% (n=30; c/i/r 5/25/0) | 3% cov 100% (n=30; c/i/r 1/29/0) | 0% cov 73% (n=30; c/i/r 0/22/8) | 100% cov 100% (n=30; c/i/r 30/0/0) | **32%** cov 93% (n=120; c/i/r 36/76/8) |

### By text (one text = one work · version · language)

**argon**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 120 | 32% | 93% | 8 | — | 14 | 62 | edition_variant 4, near_copy 1, paraphrase 5, wrong_passage 37, omission 4, wrong_locus 25 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| argon | 120 | 20,161 | 12,853 |
| **total** | 120 | 20,161 | 12,853 |
