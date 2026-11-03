| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sonnet | 0% cov 67% (n=30; c/i/r 0/20/10; minor/major 0/20) | 0% cov 53% (n=30; c/i/r 0/16/14; minor/major 0/16) | 0% cov 7% (n=30; c/i/r 0/2/28; minor/major 0/2) | 61% cov 60% (n=30; c/i/r 11/7/12; minor/major 0/7) | **20%** cov 47% (c/i/r 11/45/64; minor/major 0/45) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sonnet | cite_passage | 20 | 0 | 20 | wrong_locus 11, hedge 2, no_citation 7 |
| sonnet | complete_unit | 16 | 0 | 16 | wrong_passage 16 |
| sonnet | retrieve_quote | 2 | 0 | 2 | wrong_passage 2 |
| sonnet | verify_source | 7 | 0 | 7 | wrong_verdict 7 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sonnet | Sikhism | 0% cov 67% (n=30; c/i/r 0/20/10) | 0% cov 53% (n=30; c/i/r 0/16/14) | 0% cov 7% (n=30; c/i/r 0/2/28) | 61% cov 60% (n=30; c/i/r 11/7/12) | **20%** cov 47% (n=120; c/i/r 11/45/64) |

### By text (one text = one work · version · language)

**sonnet**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 120 | 20% | 47% | 64 | — | 0 | 45 | wrong_passage 18, wrong_locus 11, hedge 2, no_citation 7, wrong_verdict 7 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sonnet | 120 | 25,667 | 43,657 |
| **total** | 120 | 25,667 | 43,657 |
