| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| luna | 7% cov 100% (n=30; c/i/r 2/28/0; minor/major 0/28) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 2/28) | 0% cov 20% (n=30; c/i/r 0/6/24; minor/major 0/6) | 70% cov 100% (n=30; c/i/r 21/9/0; minor/major 0/9) | **24%** cov 80% (c/i/r 23/73/24; minor/major 2/71) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| luna | cite_passage | 28 | 0 | 28 | wrong_locus 28 |
| luna | complete_unit | 30 | 2 | 28 | paraphrase 2, wrong_passage 28 |
| luna | retrieve_quote | 6 | 0 | 6 | wrong_passage 6 |
| luna | verify_source | 9 | 0 | 9 | wrong_verdict 9 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| luna | Sikhism | 7% cov 100% (n=30; c/i/r 2/28/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 20% (n=30; c/i/r 0/6/24) | 70% cov 100% (n=30; c/i/r 21/9/0) | **24%** cov 80% (n=120; c/i/r 23/73/24) |

### By text (one text = one work · version · language)

**luna**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 120 | 24% | 80% | 24 | — | 2 | 71 | paraphrase 2, wrong_passage 34, wrong_locus 28, wrong_verdict 9 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| luna | 120 | 12,739 | 2,317 |
| **total** | 120 | 12,739 | 2,317 |
