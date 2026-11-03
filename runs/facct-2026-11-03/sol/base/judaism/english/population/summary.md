| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sol | 63% cov 100% (n=30; c/i/r 19/11/0; minor/major 0/11) | 0% cov 3% (n=30; c/i/r 0/1/29; minor/major 1/0) | n/a cov 0% (n=30; c/i/r 0/0/30; minor/major 0/0) | 87% cov 100% (n=30; c/i/r 26/4/0; minor/major 0/4) | **74%** cov 51% (c/i/r 45/16/59; minor/major 1/15) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sol | cite_passage | 11 | 0 | 11 | wrong_locus 11 |
| sol | complete_unit | 1 | 1 | 0 | omission 1 |
| sol | verify_source | 4 | 0 | 4 | wrong_verdict 4 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sol | Judaism | 63% cov 100% (n=30; c/i/r 19/11/0) | 0% cov 3% (n=30; c/i/r 0/1/29) | n/a cov 0% (n=30; c/i/r 0/0/30) | 87% cov 100% (n=30; c/i/r 26/4/0) | **74%** cov 51% (n=120; c/i/r 45/16/59) |

### By text (one text = one work · version · language)

**sol**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - English, en) | 120 | 74% | 51% | 59 | — | 1 | 15 | omission 1, wrong_locus 11, wrong_verdict 4 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sol | 120 | 13,115 | 30,889 |
| **total** | 120 | 13,115 | 30,889 |
