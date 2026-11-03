| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| haiku | 0% cov 60% (n=30; c/i/r 0/18/12; minor/major 0/18) | 0% cov 83% (n=30; c/i/r 0/25/5; minor/major 0/25) | 0% cov 16% (n=25; c/i/r 0/4/21; minor/major 0/4) | 97% cov 97% (n=30; c/i/r 28/1/1; minor/major 0/1) | **37%** cov 66% (c/i/r 28/48/39; minor/major 0/48) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| haiku | cite_passage | 18 | 0 | 18 | wrong_locus 16, hedge 2 |
| haiku | complete_unit | 25 | 0 | 25 | wrong_passage 25 |
| haiku | retrieve_quote | 4 | 0 | 4 | wrong_passage 4 |
| haiku | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| haiku | Sikhism | 0% cov 60% (n=30; c/i/r 0/18/12) | 0% cov 83% (n=30; c/i/r 0/25/5) | 0% cov 16% (n=25; c/i/r 0/4/21) | 97% cov 97% (n=30; c/i/r 28/1/1) | **37%** cov 66% (n=115; c/i/r 28/48/39) |

### By text (one text = one work · version · language)

**haiku**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 115 | 37% | 66% | 39 | — | 0 | 48 | wrong_passage 29, wrong_locus 16, hedge 2, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| haiku | 115 | 30,129 | 75,490 |
| **total** | 115 | 30,129 | 75,490 |
