| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| kimi | 3% cov 100% (n=30; c/i/r 1/29/0; minor/major 0/29) | 0% cov 97% (n=30; c/i/r 0/29/1; minor/major 0/29) | 0% cov 100% (n=25; c/i/r 0/25/0; minor/major 0/25) | 73% cov 100% (n=30; c/i/r 22/8/0; minor/major 0/8) | **20%** cov 99% (c/i/r 23/91/1; minor/major 0/91) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| kimi | cite_passage | 29 | 0 | 29 | wrong_locus 29 |
| kimi | complete_unit | 29 | 0 | 29 | wrong_passage 29 |
| kimi | retrieve_quote | 25 | 0 | 25 | wrong_passage 25 |
| kimi | verify_source | 8 | 0 | 8 | wrong_verdict 8 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| kimi | Sikhism | 3% cov 100% (n=30; c/i/r 1/29/0) | 0% cov 97% (n=30; c/i/r 0/29/1) | 0% cov 100% (n=25; c/i/r 0/25/0) | 73% cov 100% (n=30; c/i/r 22/8/0) | **20%** cov 99% (n=115; c/i/r 23/91/1) |

### By text (one text = one work · version · language)

**kimi**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 115 | 20% | 99% | 1 | — | 0 | 91 | wrong_passage 54, wrong_locus 29, wrong_verdict 8 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| kimi | 115 | 15,066 | 10,910 |
| **total** | 115 | 15,066 | 10,910 |
