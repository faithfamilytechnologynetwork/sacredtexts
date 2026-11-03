| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemma-31b | 7% cov 100% (n=30; c/i/r 2/28/0; minor/major 0/28) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 3/27) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 2/28) | 73% cov 100% (n=30; c/i/r 22/8/0; minor/major 0/8) | **20%** cov 100% (c/i/r 24/96/0; minor/major 5/91) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gemma-31b | cite_passage | 28 | 0 | 28 | wrong_locus 28 |
| gemma-31b | complete_unit | 30 | 3 | 27 | paraphrase 1, wrong_passage 27, omission 2 |
| gemma-31b | retrieve_quote | 30 | 2 | 28 | paraphrase 2, wrong_passage 28 |
| gemma-31b | verify_source | 8 | 0 | 8 | wrong_verdict 8 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemma-31b | Book of Mormon | 7% cov 100% (n=30; c/i/r 2/28/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 73% cov 100% (n=30; c/i/r 22/8/0) | **20%** cov 100% (n=120; c/i/r 24/96/0) |

### By text (one text = one work · version · language)

**gemma-31b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Book of Mormon (2013 edition, en) | 120 | 20% | 100% | 0 | — | 5 | 91 | paraphrase 3, wrong_passage 55, omission 2, wrong_locus 28, wrong_verdict 8 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemma-31b | 120 | 10,463 | 1,709 |
| **total** | 120 | 10,463 | 1,709 |
