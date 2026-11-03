| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| astra | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 0% cov 3% (n=30; c/i/r 0/1/29; minor/major 0/1) | n/a cov 0% (n=30; c/i/r 0/0/30; minor/major 0/0) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **98%** cov 51% (c/i/r 60/1/59; minor/major 0/1) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| astra | complete_unit | 1 | 0 | 1 | wrong_passage 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| astra | Christianity | 100% cov 100% (n=30; c/i/r 30/0/0) | 0% cov 3% (n=30; c/i/r 0/1/29) | n/a cov 0% (n=30; c/i/r 0/0/30) | 100% cov 100% (n=30; c/i/r 30/0/0) | **98%** cov 51% (n=120; c/i/r 60/1/59) |

### By text (one text = one work · version · language)

**astra**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (NRSV, en) | 120 | 98% | 51% | 59 | — | 0 | 1 | wrong_passage 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| astra | 120 | 6,864 | 5,789 |
| **total** | 120 | 6,864 | 5,789 |
