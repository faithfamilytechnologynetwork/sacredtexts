| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| fable | 23% cov 100% (n=30; c/i/r 7/23/0; minor/major 0/23) | 67% cov 100% (n=30; c/i/r 20/10/0; minor/major 5/5) | 0% cov 40% (n=30; c/i/r 0/12/18; minor/major 0/12) | 97% cov 97% (n=30; c/i/r 28/1/1; minor/major 0/1) | **54%** cov 84% (c/i/r 55/46/19; minor/major 5/41) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| fable | cite_passage | 23 | 0 | 23 | wrong_locus 23 |
| fable | complete_unit | 10 | 5 | 5 | diacritic_only 1, edition_variant 1, paraphrase 1, wrong_passage 5, omission 2, addition 3 |
| fable | retrieve_quote | 12 | 0 | 12 | wrong_passage 12 |
| fable | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| fable | Sikhism | 23% cov 100% (n=30; c/i/r 7/23/0) | 67% cov 100% (n=30; c/i/r 20/10/0) | 0% cov 40% (n=30; c/i/r 0/12/18) | 97% cov 97% (n=30; c/i/r 28/1/1) | **54%** cov 84% (n=120; c/i/r 55/46/19) |

### By text (one text = one work · version · language)

**fable**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 120 | 54% | 84% | 19 | — | 5 | 41 | diacritic_only 1, edition_variant 1, paraphrase 1, wrong_passage 17, omission 2, addition 3, wrong_locus 23, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| fable | 120 | 30,418 | 196,765 |
| **total** | 120 | 30,418 | 196,765 |
