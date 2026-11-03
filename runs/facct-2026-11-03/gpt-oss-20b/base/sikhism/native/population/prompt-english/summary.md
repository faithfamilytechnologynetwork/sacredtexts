| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gpt-oss-20b | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 0% cov 3% (n=30; c/i/r 0/1/29; minor/major 0/1) | 60% cov 100% (n=30; c/i/r 18/12/0; minor/major 0/12) | **20%** cov 76% (c/i/r 18/73/29; minor/major 0/73) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gpt-oss-20b | cite_passage | 30 | 0 | 30 | wrong_locus 30 |
| gpt-oss-20b | complete_unit | 30 | 0 | 30 | wrong_passage 30 |
| gpt-oss-20b | retrieve_quote | 1 | 0 | 1 | wrong_passage 1 |
| gpt-oss-20b | verify_source | 12 | 0 | 12 | wrong_verdict 12 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gpt-oss-20b | Sikhism | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 3% (n=30; c/i/r 0/1/29) | 60% cov 100% (n=30; c/i/r 18/12/0) | **20%** cov 76% (n=120; c/i/r 18/73/29) |

### By text (one text = one work · version · language)

**gpt-oss-20b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 120 | 20% | 76% | 29 | — | 0 | 73 | wrong_passage 31, wrong_locus 30, wrong_verdict 12 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gpt-oss-20b | 120 | 20,073 | 76,733 |
| **total** | 120 | 20,073 | 76,733 |
