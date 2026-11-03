| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sonnet | 0% cov 87% (n=30; c/i/r 0/26/4; minor/major 0/26) | 0% cov 90% (n=30; c/i/r 0/27/3; minor/major 0/27) | n/a cov 0% (n=25; c/i/r 0/0/25; minor/major 0/0) | 70% cov 100% (n=30; c/i/r 21/9/0; minor/major 0/9) | **25%** cov 72% (c/i/r 21/62/32; minor/major 0/62) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sonnet | cite_passage | 26 | 0 | 26 | wrong_locus 16, hedge 2, no_citation 8 |
| sonnet | complete_unit | 27 | 0 | 27 | wrong_passage 27 |
| sonnet | verify_source | 9 | 0 | 9 | wrong_verdict 9 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sonnet | Sikhism | 0% cov 87% (n=30; c/i/r 0/26/4) | 0% cov 90% (n=30; c/i/r 0/27/3) | n/a cov 0% (n=25; c/i/r 0/0/25) | 70% cov 100% (n=30; c/i/r 21/9/0) | **25%** cov 72% (n=115; c/i/r 21/62/32) |

### By text (one text = one work · version · language)

**sonnet**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 115 | 25% | 72% | 32 | — | 0 | 62 | wrong_passage 27, wrong_locus 16, hedge 2, no_citation 8, wrong_verdict 9 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sonnet | 115 | 30,359 | 104,919 |
| **total** | 115 | 30,359 | 104,919 |
