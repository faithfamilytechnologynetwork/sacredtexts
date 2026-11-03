| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| deepseek-v4-pro | 20% cov 100% (n=30; c/i/r 6/24/0; minor/major 0/24) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 11/19) | 0% cov 90% (n=30; c/i/r 0/27/3; minor/major 2/25) | 73% cov 100% (n=30; c/i/r 22/8/0; minor/major 0/8) | **24%** cov 98% (c/i/r 28/89/3; minor/major 13/76) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| deepseek-v4-pro | cite_passage | 24 | 0 | 24 | wrong_locus 24 |
| deepseek-v4-pro | complete_unit | 30 | 11 | 19 | paraphrase 4, wrong_passage 19, omission 7 |
| deepseek-v4-pro | retrieve_quote | 27 | 2 | 25 | paraphrase 2, wrong_passage 25 |
| deepseek-v4-pro | verify_source | 8 | 0 | 8 | wrong_verdict 8 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| deepseek-v4-pro | Judaism | 20% cov 100% (n=30; c/i/r 6/24/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 90% (n=30; c/i/r 0/27/3) | 73% cov 100% (n=30; c/i/r 22/8/0) | **24%** cov 98% (n=120; c/i/r 28/89/3) |

### By text (one text = one work · version · language)

**deepseek-v4-pro**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - English, en) | 120 | 24% | 98% | 3 | — | 13 | 76 | paraphrase 6, wrong_passage 44, omission 7, wrong_locus 24, wrong_verdict 8 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| deepseek-v4-pro | 120 | 12,594 | 4,711 |
| **total** | 120 | 12,594 | 4,711 |
