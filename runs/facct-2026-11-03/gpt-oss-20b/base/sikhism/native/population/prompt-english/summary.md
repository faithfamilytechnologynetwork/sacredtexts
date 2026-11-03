| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gpt-oss-20b | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 0% cov 20% (n=25; c/i/r 0/5/20; minor/major 0/5) | 60% cov 100% (n=30; c/i/r 18/12/0; minor/major 0/12) | **19%** cov 83% (c/i/r 18/77/20; minor/major 0/77) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gpt-oss-20b | cite_passage | 30 | 0 | 30 | wrong_locus 30 |
| gpt-oss-20b | complete_unit | 30 | 0 | 30 | wrong_passage 30 |
| gpt-oss-20b | retrieve_quote | 5 | 0 | 5 | wrong_passage 5 |
| gpt-oss-20b | verify_source | 12 | 0 | 12 | wrong_verdict 12 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gpt-oss-20b | Sikhism | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 20% (n=25; c/i/r 0/5/20) | 60% cov 100% (n=30; c/i/r 18/12/0) | **19%** cov 83% (n=115; c/i/r 18/77/20) |

### By text (one text = one work · version · language)

**gpt-oss-20b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 115 | 19% | 83% | 20 | — | 0 | 77 | wrong_passage 35, wrong_locus 30, wrong_verdict 12 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gpt-oss-20b | 115 | 19,410 | 84,427 |
| **total** | 115 | 19,410 | 84,427 |
