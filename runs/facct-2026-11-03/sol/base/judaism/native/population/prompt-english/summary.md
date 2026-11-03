| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sol | 60% cov 100% (n=30; c/i/r 18/12/0; minor/major 0/12) | 33% cov 100% (n=30; c/i/r 10/20/0; minor/major 14/6) | 6% cov 57% (n=30; c/i/r 1/16/13; minor/major 3/13) | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | **54%** cov 89% (c/i/r 58/49/13; minor/major 17/32) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sol | cite_passage | 12 | 0 | 12 | wrong_locus 2, no_citation 10 |
| sol | complete_unit | 20 | 14 | 6 | edition_variant 7, paraphrase 3, wrong_passage 6, omission 4, addition 1 |
| sol | retrieve_quote | 16 | 3 | 13 | near_copy 2, paraphrase 1, wrong_passage 13 |
| sol | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sol | Judaism | 60% cov 100% (n=30; c/i/r 18/12/0) | 33% cov 100% (n=30; c/i/r 10/20/0) | 6% cov 57% (n=30; c/i/r 1/16/13) | 97% cov 100% (n=30; c/i/r 29/1/0) | **54%** cov 89% (n=120; c/i/r 58/49/13) |

### By text (one text = one work · version · language)

**sol**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 54% | 89% | 13 | — | 17 | 32 | edition_variant 7, near_copy 2, paraphrase 4, wrong_passage 19, omission 4, addition 1, wrong_locus 2, no_citation 10, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sol | 120 | 12,908 | 58,903 |
| **total** | 120 | 12,908 | 58,903 |
