| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| fable | 30% cov 100% (n=30; c/i/r 9/21/0; minor/major 0/21) | 67% cov 100% (n=30; c/i/r 20/10/0; minor/major 5/5) | 14% cov 88% (n=25; c/i/r 3/19/3; minor/major 0/19) | 97% cov 97% (n=30; c/i/r 28/1/1; minor/major 0/1) | **54%** cov 97% (c/i/r 60/51/4; minor/major 5/46) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| fable | cite_passage | 21 | 0 | 21 | wrong_locus 21 |
| fable | complete_unit | 10 | 5 | 5 | diacritic_only 1, edition_variant 1, paraphrase 1, wrong_passage 5, omission 2, addition 3 |
| fable | retrieve_quote | 19 | 0 | 19 | wrong_passage 19, addition 2 |
| fable | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| fable | Sikhism | 30% cov 100% (n=30; c/i/r 9/21/0) | 67% cov 100% (n=30; c/i/r 20/10/0) | 14% cov 88% (n=25; c/i/r 3/19/3) | 97% cov 97% (n=30; c/i/r 28/1/1) | **54%** cov 97% (n=115; c/i/r 60/51/4) |

### By text (one text = one work · version · language)

**fable**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 115 | 54% | 97% | 4 | — | 5 | 46 | diacritic_only 1, edition_variant 1, paraphrase 1, wrong_passage 24, omission 2, addition 5, wrong_locus 21, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| fable | 115 | 30,359 | 170,035 |
| **total** | 115 | 30,359 | 170,035 |
