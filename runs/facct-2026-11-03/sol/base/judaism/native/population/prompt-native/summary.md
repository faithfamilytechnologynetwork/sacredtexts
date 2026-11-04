| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sol | 53% cov 100% (n=30; c/i/r 16/14/0; minor/major 0/14) | 37% cov 100% (n=30; c/i/r 11/19/0; minor/major 12/7) | 11% cov 60% (n=30; c/i/r 2/16/12; minor/major 6/10) | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | **54%** cov 90% (c/i/r 58/50/12; minor/major 18/32) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sol | cite_passage | 14 | 0 | 14 | wrong_locus 14 |
| sol | complete_unit | 19 | 12 | 7 | edition_variant 5, near_copy 1, paraphrase 2, wrong_passage 7, omission 4, addition 2 |
| sol | retrieve_quote | 16 | 6 | 10 | edition_variant 1, paraphrase 5, wrong_passage 10, addition 1 |
| sol | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sol | Judaism | 53% cov 100% (n=30; c/i/r 16/14/0) | 37% cov 100% (n=30; c/i/r 11/19/0) | 11% cov 60% (n=30; c/i/r 2/16/12) | 97% cov 100% (n=30; c/i/r 29/1/0) | **54%** cov 90% (n=120; c/i/r 58/50/12) |

### By text (one text = one work · version · language)

**sol**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 54% | 90% | 12 | — | 18 | 32 | edition_variant 6, near_copy 1, paraphrase 7, wrong_passage 17, omission 4, addition 3, wrong_locus 14, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sol | 120 | 10,488 | 51,648 |
| **total** | 120 | 10,488 | 51,648 |
