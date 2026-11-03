| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sol | 50% cov 100% (n=30; c/i/r 15/15/0; minor/major 0/15) | 33% cov 100% (n=30; c/i/r 10/20/0; minor/major 15/5) | 5% cov 67% (n=30; c/i/r 1/19/10; minor/major 6/13) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **51%** cov 92% (c/i/r 56/54/10; minor/major 21/33) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sol | cite_passage | 15 | 0 | 15 | wrong_locus 15 |
| sol | complete_unit | 20 | 15 | 5 | edition_variant 5, paraphrase 7, wrong_passage 5, omission 3 |
| sol | retrieve_quote | 19 | 6 | 13 | edition_variant 1, near_copy 1, paraphrase 4, wrong_passage 13 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sol | Judaism | 50% cov 100% (n=30; c/i/r 15/15/0) | 33% cov 100% (n=30; c/i/r 10/20/0) | 5% cov 67% (n=30; c/i/r 1/19/10) | 100% cov 100% (n=30; c/i/r 30/0/0) | **51%** cov 92% (n=120; c/i/r 56/54/10) |

### By text (one text = one work · version · language)

**sol**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 51% | 92% | 10 | — | 21 | 33 | edition_variant 6, near_copy 1, paraphrase 11, wrong_passage 18, omission 3, wrong_locus 15 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sol | 120 | 11,478 | 60,540 |
| **total** | 120 | 11,478 | 60,540 |
