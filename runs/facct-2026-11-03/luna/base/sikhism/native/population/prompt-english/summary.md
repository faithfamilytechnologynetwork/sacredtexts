| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| luna | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 2/28) | 0% cov 44% (n=25; c/i/r 0/11/14; minor/major 0/11) | 70% cov 100% (n=30; c/i/r 21/9/0; minor/major 0/9) | **21%** cov 88% (c/i/r 21/80/14; minor/major 2/78) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| luna | cite_passage | 30 | 0 | 30 | wrong_locus 30 |
| luna | complete_unit | 30 | 2 | 28 | paraphrase 2, wrong_passage 28 |
| luna | retrieve_quote | 11 | 0 | 11 | wrong_passage 11 |
| luna | verify_source | 9 | 0 | 9 | wrong_verdict 9 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| luna | Sikhism | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 44% (n=25; c/i/r 0/11/14) | 70% cov 100% (n=30; c/i/r 21/9/0) | **21%** cov 88% (n=115; c/i/r 21/80/14) |

### By text (one text = one work · version · language)

**luna**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 115 | 21% | 88% | 14 | — | 2 | 78 | paraphrase 2, wrong_passage 39, wrong_locus 30, wrong_verdict 9 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| luna | 115 | 12,397 | 1,895 |
| **total** | 115 | 12,397 | 1,895 |
