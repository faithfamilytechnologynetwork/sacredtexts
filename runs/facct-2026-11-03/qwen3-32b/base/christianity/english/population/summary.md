| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| qwen3-32b | 57% cov 100% (n=30; c/i/r 17/13/0; minor/major 0/13) | 17% cov 100% (n=30; c/i/r 5/25/0; minor/major 11/14) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 14/16) | 80% cov 100% (n=30; c/i/r 24/6/0; minor/major 0/6) | **38%** cov 100% (c/i/r 46/74/0; minor/major 25/49) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| qwen3-32b | cite_passage | 13 | 0 | 13 | wrong_locus 13 |
| qwen3-32b | complete_unit | 25 | 11 | 14 | edition_variant 2, paraphrase 8, wrong_passage 14, omission 1, addition 1 |
| qwen3-32b | retrieve_quote | 30 | 14 | 16 | edition_variant 1, near_copy 3, paraphrase 9, wrong_passage 16, omission 1 |
| qwen3-32b | verify_source | 6 | 0 | 6 | wrong_verdict 6 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| qwen3-32b | Christianity | 57% cov 100% (n=30; c/i/r 17/13/0) | 17% cov 100% (n=30; c/i/r 5/25/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 80% cov 100% (n=30; c/i/r 24/6/0) | **38%** cov 100% (n=120; c/i/r 46/74/0) |

### By text (one text = one work · version · language)

**qwen3-32b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (NRSV, en) | 120 | 38% | 100% | 0 | — | 25 | 49 | edition_variant 3, near_copy 3, paraphrase 17, wrong_passage 30, omission 2, addition 1, wrong_locus 13, wrong_verdict 6 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| qwen3-32b | 120 | 7,410 | 75,176 |
| **total** | 120 | 7,410 | 75,176 |
