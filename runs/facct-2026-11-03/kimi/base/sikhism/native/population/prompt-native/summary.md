| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| kimi | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 0% cov 88% (n=25; c/i/r 0/22/3; minor/major 0/22) | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | **26%** cov 97% (c/i/r 29/83/3; minor/major 0/83) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| kimi | cite_passage | 30 | 0 | 30 | wrong_locus 30 |
| kimi | complete_unit | 30 | 0 | 30 | wrong_passage 30 |
| kimi | retrieve_quote | 22 | 0 | 22 | wrong_passage 22 |
| kimi | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| kimi | Sikhism | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 88% (n=25; c/i/r 0/22/3) | 97% cov 100% (n=30; c/i/r 29/1/0) | **26%** cov 97% (n=115; c/i/r 29/83/3) |

### By text (one text = one work · version · language)

**kimi**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 115 | 26% | 97% | 3 | — | 0 | 83 | wrong_passage 52, wrong_locus 30, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| kimi | 115 | 14,545 | 17,653 |
| **total** | 115 | 14,545 | 17,653 |
