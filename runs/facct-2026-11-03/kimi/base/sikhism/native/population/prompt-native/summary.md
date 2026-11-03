| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| kimi | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 1/29) | 0% cov 93% (n=30; c/i/r 0/28/2; minor/major 0/28) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **25%** cov 98% (c/i/r 30/88/2; minor/major 1/87) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| kimi | cite_passage | 30 | 0 | 30 | wrong_locus 29, no_citation 1 |
| kimi | complete_unit | 30 | 1 | 29 | wrong_passage 29, omission 1 |
| kimi | retrieve_quote | 28 | 0 | 28 | wrong_passage 28 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| kimi | Sikhism | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 93% (n=30; c/i/r 0/28/2) | 100% cov 100% (n=30; c/i/r 30/0/0) | **25%** cov 98% (n=120; c/i/r 30/88/2) |

### By text (one text = one work · version · language)

**kimi**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 120 | 25% | 98% | 2 | — | 1 | 87 | wrong_passage 57, omission 1, wrong_locus 29, no_citation 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| kimi | 120 | 14,668 | 17,652 |
| **total** | 120 | 14,668 | 17,652 |
