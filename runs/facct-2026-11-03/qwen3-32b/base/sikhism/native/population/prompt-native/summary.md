| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| qwen3-32b | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 0% cov 100% (n=25; c/i/r 0/25/0; minor/major 0/25) | 90% cov 70% (n=30; c/i/r 19/2/9; minor/major 0/2) | **18%** cov 92% (c/i/r 19/87/9; minor/major 0/87) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| qwen3-32b | cite_passage | 30 | 0 | 30 | wrong_locus 30 |
| qwen3-32b | complete_unit | 30 | 0 | 30 | wrong_passage 30 |
| qwen3-32b | retrieve_quote | 25 | 0 | 25 | wrong_passage 25 |
| qwen3-32b | verify_source | 2 | 0 | 2 | wrong_verdict 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| qwen3-32b | Sikhism | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=25; c/i/r 0/25/0) | 90% cov 70% (n=30; c/i/r 19/2/9) | **18%** cov 92% (n=115; c/i/r 19/87/9) |

### By text (one text = one work · version · language)

**qwen3-32b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 115 | 18% | 92% | 9 | — | 0 | 87 | wrong_passage 55, wrong_locus 30, wrong_verdict 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| qwen3-32b | 115 | 22,667 | 96,142 |
| **total** | 115 | 22,667 | 96,142 |
