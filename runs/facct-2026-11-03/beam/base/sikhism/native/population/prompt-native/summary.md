| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| beam | 0% cov 30% (n=30; c/i/r 0/9/21; minor/major 0/9) | 0% cov 67% (n=30; c/i/r 0/20/10; minor/major 1/19) | 0% cov 13% (n=30; c/i/r 0/4/26; minor/major 0/4) | 93% cov 93% (n=30; c/i/r 26/2/2; minor/major 0/2) | **43%** cov 51% (c/i/r 26/35/59; minor/major 1/34) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| beam | cite_passage | 9 | 0 | 9 | wrong_locus 9 |
| beam | complete_unit | 20 | 1 | 19 | wrong_passage 19, omission 1 |
| beam | retrieve_quote | 4 | 0 | 4 | wrong_passage 4 |
| beam | verify_source | 2 | 0 | 2 | wrong_verdict 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| beam | Sikhism | 0% cov 30% (n=30; c/i/r 0/9/21) | 0% cov 67% (n=30; c/i/r 0/20/10) | 0% cov 13% (n=30; c/i/r 0/4/26) | 93% cov 93% (n=30; c/i/r 26/2/2) | **43%** cov 51% (n=120; c/i/r 26/35/59) |

### By text (one text = one work · version · language)

**beam**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 120 | 43% | 51% | 59 | — | 1 | 34 | wrong_passage 23, omission 1, wrong_locus 9, wrong_verdict 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| beam | 120 | 27,121 | 168,844 |
| **total** | 120 | 27,121 | 168,844 |
