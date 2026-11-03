| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemma-31b | 40% cov 100% (n=30; c/i/r 12/18/0; minor/major 0/18) | 3% cov 100% (n=30; c/i/r 1/29/0; minor/major 8/21) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 12/18) | 73% cov 100% (n=30; c/i/r 22/8/0; minor/major 0/8) | **29%** cov 100% (c/i/r 35/85/0; minor/major 20/65) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gemma-31b | cite_passage | 18 | 0 | 18 | wrong_locus 18 |
| gemma-31b | complete_unit | 29 | 8 | 21 | paraphrase 6, wrong_passage 21, omission 2 |
| gemma-31b | retrieve_quote | 30 | 12 | 18 | near_copy 2, paraphrase 10, wrong_passage 18 |
| gemma-31b | verify_source | 8 | 0 | 8 | wrong_verdict 8 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemma-31b | Christianity | 40% cov 100% (n=30; c/i/r 12/18/0) | 3% cov 100% (n=30; c/i/r 1/29/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 73% cov 100% (n=30; c/i/r 22/8/0) | **29%** cov 100% (n=120; c/i/r 35/85/0) |

### By text (one text = one work · version · language)

**gemma-31b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (NRSV, en) | 120 | 29% | 100% | 0 | — | 20 | 65 | near_copy 2, paraphrase 16, wrong_passage 39, omission 2, wrong_locus 18, wrong_verdict 8 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemma-31b | 120 | 7,741 | 1,583 |
| **total** | 120 | 7,741 | 1,583 |
