| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| haiku | 0% cov 23% (n=30; c/i/r 0/7/23; minor/major 0/7) | 0% cov 80% (n=30; c/i/r 0/24/6; minor/major 1/23) | n/a cov 0% (n=25; c/i/r 0/0/25; minor/major 0/0) | 53% cov 63% (n=30; c/i/r 10/9/11; minor/major 0/9) | **20%** cov 43% (c/i/r 10/40/65; minor/major 1/39) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| haiku | cite_passage | 7 | 0 | 7 | wrong_locus 7 |
| haiku | complete_unit | 24 | 1 | 23 | paraphrase 1, wrong_passage 23 |
| haiku | verify_source | 9 | 0 | 9 | wrong_verdict 9 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| haiku | Sikhism | 0% cov 23% (n=30; c/i/r 0/7/23) | 0% cov 80% (n=30; c/i/r 0/24/6) | n/a cov 0% (n=25; c/i/r 0/0/25) | 53% cov 63% (n=30; c/i/r 10/9/11) | **20%** cov 43% (n=115; c/i/r 10/40/65) |

### By text (one text = one work · version · language)

**haiku**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 115 | 20% | 43% | 65 | — | 1 | 39 | paraphrase 1, wrong_passage 23, wrong_locus 7, wrong_verdict 9 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| haiku | 115 | 24,900 | 18,896 |
| **total** | 115 | 24,900 | 18,896 |
