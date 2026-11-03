| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| qwen3-32b | 33% cov 100% (n=9; c/i/r 3/6/0; minor/major 0/6) | 0% cov 100% (n=9; c/i/r 0/9/0; minor/major 3/6) | 0% cov 100% (n=9; c/i/r 0/9/0; minor/major 1/8) | 100% cov 100% (n=9; c/i/r 9/0/0; minor/major 0/0) | **33%** cov 100% (c/i/r 12/24/0; minor/major 4/20) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| qwen3-32b | cite_passage | 6 | 0 | 6 | wrong_locus 6 |
| qwen3-32b | complete_unit | 9 | 3 | 6 | paraphrase 3, wrong_passage 6 |
| qwen3-32b | retrieve_quote | 9 | 1 | 8 | paraphrase 1, wrong_passage 8 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| qwen3-32b | Christianity | 33% cov 100% (n=9; c/i/r 3/6/0) | 0% cov 100% (n=9; c/i/r 0/9/0) | 0% cov 100% (n=9; c/i/r 0/9/0) | 100% cov 100% (n=9; c/i/r 9/0/0) | **33%** cov 100% (n=36; c/i/r 12/24/0) |

### By text (one text = one work · version · language)

**qwen3-32b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (the Greek New Testament (Scrivener 1894), grc) | 36 | 33% | 100% | 0 | — | 4 | 20 | paraphrase 4, wrong_passage 14, wrong_locus 6 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| qwen3-32b | 36 | 6,234 | 11,247 |
| **total** | 36 | 6,234 | 11,247 |
