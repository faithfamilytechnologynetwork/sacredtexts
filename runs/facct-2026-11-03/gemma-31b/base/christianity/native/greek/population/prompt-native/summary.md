| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemma-31b | 33% cov 100% (n=9; c/i/r 3/6/0; minor/major 0/6) | 0% cov 100% (n=9; c/i/r 0/9/0; minor/major 0/9) | 0% cov 100% (n=9; c/i/r 0/9/0; minor/major 3/6) | 89% cov 100% (n=9; c/i/r 8/1/0; minor/major 0/1) | **31%** cov 100% (c/i/r 11/25/0; minor/major 3/22) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gemma-31b | cite_passage | 6 | 0 | 6 | wrong_locus 6 |
| gemma-31b | complete_unit | 9 | 0 | 9 | wrong_passage 9 |
| gemma-31b | retrieve_quote | 9 | 3 | 6 | paraphrase 3, wrong_passage 6 |
| gemma-31b | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemma-31b | Christianity | 33% cov 100% (n=9; c/i/r 3/6/0) | 0% cov 100% (n=9; c/i/r 0/9/0) | 0% cov 100% (n=9; c/i/r 0/9/0) | 89% cov 100% (n=9; c/i/r 8/1/0) | **31%** cov 100% (n=36; c/i/r 11/25/0) |

### By text (one text = one work · version · language)

**gemma-31b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (the Greek New Testament (Scrivener 1894), grc) | 36 | 31% | 100% | 0 | — | 3 | 22 | paraphrase 3, wrong_passage 15, wrong_locus 6, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemma-31b | 36 | 3,714 | 752 |
| **total** | 36 | 3,714 | 752 |
