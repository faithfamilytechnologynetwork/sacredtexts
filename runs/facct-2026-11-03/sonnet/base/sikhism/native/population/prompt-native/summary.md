| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sonnet | 6% cov 60% (n=30; c/i/r 1/17/12; minor/major 0/17) | 0% cov 90% (n=30; c/i/r 0/27/3; minor/major 0/27) | 0% cov 17% (n=30; c/i/r 0/5/25; minor/major 0/5) | 70% cov 100% (n=30; c/i/r 21/9/0; minor/major 0/9) | **28%** cov 67% (c/i/r 22/58/40; minor/major 0/58) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sonnet | cite_passage | 17 | 0 | 17 | wrong_locus 8, no_citation 9 |
| sonnet | complete_unit | 27 | 0 | 27 | wrong_passage 27 |
| sonnet | retrieve_quote | 5 | 0 | 5 | wrong_passage 5 |
| sonnet | verify_source | 9 | 0 | 9 | wrong_verdict 9 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sonnet | Sikhism | 6% cov 60% (n=30; c/i/r 1/17/12) | 0% cov 90% (n=30; c/i/r 0/27/3) | 0% cov 17% (n=30; c/i/r 0/5/25) | 70% cov 100% (n=30; c/i/r 21/9/0) | **28%** cov 67% (n=120; c/i/r 22/58/40) |

### By text (one text = one work · version · language)

**sonnet**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 120 | 28% | 67% | 40 | — | 0 | 58 | wrong_passage 32, wrong_locus 8, no_citation 9, wrong_verdict 9 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sonnet | 120 | 30,418 | 112,283 |
| **total** | 120 | 30,418 | 112,283 |
