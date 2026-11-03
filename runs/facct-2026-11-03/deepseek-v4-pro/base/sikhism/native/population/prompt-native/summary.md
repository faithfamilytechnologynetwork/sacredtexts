| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| deepseek-v4-pro | 3% cov 100% (n=30; c/i/r 1/29/0; minor/major 0/29) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 4/26) | 0% cov 96% (n=25; c/i/r 0/24/1; minor/major 0/24) | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | **26%** cov 99% (c/i/r 30/84/1; minor/major 4/80) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| deepseek-v4-pro | cite_passage | 29 | 0 | 29 | wrong_locus 29 |
| deepseek-v4-pro | complete_unit | 30 | 4 | 26 | paraphrase 1, wrong_passage 26, omission 3 |
| deepseek-v4-pro | retrieve_quote | 24 | 0 | 24 | wrong_passage 24 |
| deepseek-v4-pro | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| deepseek-v4-pro | Sikhism | 3% cov 100% (n=30; c/i/r 1/29/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 96% (n=25; c/i/r 0/24/1) | 97% cov 100% (n=30; c/i/r 29/1/0) | **26%** cov 99% (n=115; c/i/r 30/84/1) |

### By text (one text = one work · version · language)

**deepseek-v4-pro**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 115 | 26% | 99% | 1 | — | 4 | 80 | paraphrase 1, wrong_passage 50, omission 3, wrong_locus 29, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| deepseek-v4-pro | 115 | 14,332 | 10,556 |
| **total** | 115 | 14,332 | 10,556 |
