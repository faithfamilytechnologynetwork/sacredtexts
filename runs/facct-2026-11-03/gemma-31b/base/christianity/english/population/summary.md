| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemma-31b | 40% cov 100% (n=30; c/i/r 12/18/0; minor/major 0/18) | 7% cov 100% (n=30; c/i/r 2/28/0; minor/major 7/21) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 12/18) | 73% cov 100% (n=30; c/i/r 22/8/0; minor/major 0/8) | **30%** cov 100% (c/i/r 36/84/0; minor/major 19/65) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gemma-31b | cite_passage | 18 | 0 | 18 | wrong_locus 18 |
| gemma-31b | complete_unit | 28 | 7 | 21 | paraphrase 5, wrong_passage 21, omission 2 |
| gemma-31b | retrieve_quote | 30 | 12 | 18 | near_copy 2, paraphrase 10, wrong_passage 18 |
| gemma-31b | verify_source | 8 | 0 | 8 | wrong_verdict 8 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemma-31b | Christianity | 40% cov 100% (n=30; c/i/r 12/18/0) | 7% cov 100% (n=30; c/i/r 2/28/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 73% cov 100% (n=30; c/i/r 22/8/0) | **30%** cov 100% (n=120; c/i/r 36/84/0) |

### By text (one text = one work · version · language)

**gemma-31b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (NRSV, en) | 120 | 30% | 100% | 0 | — | 19 | 65 | near_copy 2, paraphrase 15, wrong_passage 39, omission 2, wrong_locus 18, wrong_verdict 8 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemma-31b | 120 | 7,741 | 1,583 |
| **total** | 120 | 7,741 | 1,583 |
