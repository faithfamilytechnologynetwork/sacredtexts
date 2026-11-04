| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sol | 63% cov 100% (n=30; c/i/r 19/11/0; minor/major 0/11) | 47% cov 100% (n=30; c/i/r 14/16/0; minor/major 10/6) | 17% cov 77% (n=30; c/i/r 4/19/7; minor/major 2/17) | 93% cov 100% (n=30; c/i/r 28/2/0; minor/major 0/2) | **58%** cov 94% (c/i/r 65/48/7; minor/major 12/36) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sol | cite_passage | 11 | 0 | 11 | wrong_locus 11 |
| sol | complete_unit | 16 | 10 | 6 | edition_variant 3, near_copy 1, paraphrase 3, wrong_passage 6, omission 3, addition 1 |
| sol | retrieve_quote | 19 | 2 | 17 | paraphrase 2, wrong_passage 17, addition 2 |
| sol | verify_source | 2 | 0 | 2 | wrong_verdict 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sol | Judaism | 63% cov 100% (n=30; c/i/r 19/11/0) | 47% cov 100% (n=30; c/i/r 14/16/0) | 17% cov 77% (n=30; c/i/r 4/19/7) | 93% cov 100% (n=30; c/i/r 28/2/0) | **58%** cov 94% (n=120; c/i/r 65/48/7) |

### By text (one text = one work · version · language)

**sol**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 58% | 94% | 7 | — | 12 | 36 | edition_variant 3, near_copy 1, paraphrase 5, wrong_passage 23, omission 3, addition 3, wrong_locus 11, wrong_verdict 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sol | 120 | 11,948 | 51,560 |
| **total** | 120 | 11,948 | 51,560 |
