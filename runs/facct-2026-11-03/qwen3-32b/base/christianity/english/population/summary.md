| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| qwen3-32b | 57% cov 100% (n=30; c/i/r 17/13/0; minor/major 0/13) | 7% cov 100% (n=30; c/i/r 2/28/0; minor/major 14/14) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 14/16) | 80% cov 100% (n=30; c/i/r 24/6/0; minor/major 0/6) | **36%** cov 100% (c/i/r 43/77/0; minor/major 28/49) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| qwen3-32b | cite_passage | 13 | 0 | 13 | wrong_locus 13 |
| qwen3-32b | complete_unit | 28 | 14 | 14 | edition_variant 4, paraphrase 9, wrong_passage 14, omission 1, addition 1 |
| qwen3-32b | retrieve_quote | 30 | 14 | 16 | edition_variant 1, near_copy 3, paraphrase 9, wrong_passage 16, omission 1 |
| qwen3-32b | verify_source | 6 | 0 | 6 | wrong_verdict 6 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| qwen3-32b | Christianity | 57% cov 100% (n=30; c/i/r 17/13/0) | 7% cov 100% (n=30; c/i/r 2/28/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 80% cov 100% (n=30; c/i/r 24/6/0) | **36%** cov 100% (n=120; c/i/r 43/77/0) |

### By text (one text = one work · version · language)

**qwen3-32b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (NRSV, en) | 120 | 36% | 100% | 0 | — | 28 | 49 | edition_variant 5, near_copy 3, paraphrase 18, wrong_passage 30, omission 2, addition 1, wrong_locus 13, wrong_verdict 6 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| qwen3-32b | 120 | 7,410 | 75,176 |
| **total** | 120 | 7,410 | 75,176 |
