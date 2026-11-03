| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| deepseek-v4-pro | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 4/26) | 0% cov 87% (n=30; c/i/r 0/26/4; minor/major 0/26) | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | **25%** cov 97% (c/i/r 29/87/4; minor/major 4/83) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| deepseek-v4-pro | cite_passage | 30 | 0 | 30 | wrong_locus 30 |
| deepseek-v4-pro | complete_unit | 30 | 4 | 26 | paraphrase 1, wrong_passage 26, omission 3 |
| deepseek-v4-pro | retrieve_quote | 26 | 0 | 26 | wrong_passage 26 |
| deepseek-v4-pro | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| deepseek-v4-pro | Sikhism | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 87% (n=30; c/i/r 0/26/4) | 97% cov 100% (n=30; c/i/r 29/1/0) | **25%** cov 97% (n=120; c/i/r 29/87/4) |

### By text (one text = one work · version · language)

**deepseek-v4-pro**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 120 | 25% | 97% | 4 | — | 4 | 83 | paraphrase 1, wrong_passage 52, omission 3, wrong_locus 30, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| deepseek-v4-pro | 120 | 14,441 | 25,773 |
| **total** | 120 | 14,441 | 25,773 |
