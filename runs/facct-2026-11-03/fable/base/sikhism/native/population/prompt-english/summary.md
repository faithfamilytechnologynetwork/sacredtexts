| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| fable | 13% cov 100% (n=30; c/i/r 4/26/0; minor/major 0/26) | 57% cov 100% (n=30; c/i/r 17/13/0; minor/major 10/3) | 16% cov 100% (n=25; c/i/r 4/21/0; minor/major 1/20) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **48%** cov 100% (c/i/r 55/60/0; minor/major 11/49) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| fable | cite_passage | 26 | 0 | 26 | wrong_locus 26 |
| fable | complete_unit | 13 | 10 | 3 | edition_variant 1, paraphrase 4, wrong_passage 3, omission 5 |
| fable | retrieve_quote | 21 | 1 | 20 | paraphrase 1, wrong_passage 20 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| fable | Sikhism | 13% cov 100% (n=30; c/i/r 4/26/0) | 57% cov 100% (n=30; c/i/r 17/13/0) | 16% cov 100% (n=25; c/i/r 4/21/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **48%** cov 100% (n=115; c/i/r 55/60/0) |

### By text (one text = one work · version · language)

**fable**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 115 | 48% | 100% | 0 | — | 11 | 49 | edition_variant 1, paraphrase 5, wrong_passage 23, omission 5, wrong_locus 26 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| fable | 115 | 25,130 | 136,987 |
| **total** | 115 | 25,130 | 136,987 |
