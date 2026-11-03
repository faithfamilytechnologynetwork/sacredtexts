| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemma-31b | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 0% cov 100% (n=25; c/i/r 0/25/0; minor/major 0/25) | 70% cov 100% (n=30; c/i/r 21/9/0; minor/major 0/9) | **18%** cov 100% (c/i/r 21/94/0; minor/major 0/94) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gemma-31b | cite_passage | 30 | 0 | 30 | wrong_locus 30 |
| gemma-31b | complete_unit | 30 | 0 | 30 | wrong_passage 30 |
| gemma-31b | retrieve_quote | 25 | 0 | 25 | wrong_passage 25 |
| gemma-31b | verify_source | 9 | 0 | 9 | wrong_verdict 9 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemma-31b | Sikhism | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=25; c/i/r 0/25/0) | 70% cov 100% (n=30; c/i/r 21/9/0) | **18%** cov 100% (n=115; c/i/r 21/94/0) |

### By text (one text = one work · version · language)

**gemma-31b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 115 | 18% | 100% | 0 | — | 0 | 94 | wrong_passage 55, wrong_locus 30, wrong_verdict 9 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemma-31b | 115 | 13,323 | 9,422 |
| **total** | 115 | 13,323 | 9,422 |
