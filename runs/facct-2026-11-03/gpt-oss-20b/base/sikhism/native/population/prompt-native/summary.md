| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gpt-oss-20b | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 0% cov 56% (n=25; c/i/r 0/14/11; minor/major 0/14) | 50% cov 100% (n=30; c/i/r 15/15/0; minor/major 0/15) | **14%** cov 90% (c/i/r 15/89/11; minor/major 0/89) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gpt-oss-20b | cite_passage | 30 | 0 | 30 | wrong_locus 30 |
| gpt-oss-20b | complete_unit | 30 | 0 | 30 | wrong_passage 30 |
| gpt-oss-20b | retrieve_quote | 14 | 0 | 14 | wrong_passage 14 |
| gpt-oss-20b | verify_source | 15 | 0 | 15 | wrong_verdict 15 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gpt-oss-20b | Sikhism | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 56% (n=25; c/i/r 0/14/11) | 50% cov 100% (n=30; c/i/r 15/15/0) | **14%** cov 90% (n=115; c/i/r 15/89/11) |

### By text (one text = one work · version · language)

**gpt-oss-20b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 115 | 14% | 90% | 11 | — | 0 | 89 | wrong_passage 44, wrong_locus 30, wrong_verdict 15 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gpt-oss-20b | 115 | 17,192 | 81,711 |
| **total** | 115 | 17,192 | 81,711 |
