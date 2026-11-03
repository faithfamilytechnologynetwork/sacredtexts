| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| fable | 23% cov 100% (n=30; c/i/r 7/23/0; minor/major 0/23) | 53% cov 100% (n=30; c/i/r 16/14/0; minor/major 11/3) | 12% cov 80% (n=30; c/i/r 3/21/6; minor/major 0/21) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **49%** cov 95% (c/i/r 56/58/6; minor/major 11/47) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| fable | cite_passage | 23 | 0 | 23 | wrong_locus 23 |
| fable | complete_unit | 14 | 11 | 3 | edition_variant 2, paraphrase 4, wrong_passage 3, omission 5 |
| fable | retrieve_quote | 21 | 0 | 21 | wrong_passage 21 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| fable | Sikhism | 23% cov 100% (n=30; c/i/r 7/23/0) | 53% cov 100% (n=30; c/i/r 16/14/0) | 12% cov 80% (n=30; c/i/r 3/21/6) | 100% cov 100% (n=30; c/i/r 30/0/0) | **49%** cov 95% (n=120; c/i/r 56/58/6) |

### By text (one text = one work · version · language)

**fable**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 120 | 49% | 95% | 6 | — | 11 | 47 | edition_variant 2, paraphrase 4, wrong_passage 24, omission 5, wrong_locus 23 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| fable | 120 | 25,667 | 178,700 |
| **total** | 120 | 25,667 | 178,700 |
