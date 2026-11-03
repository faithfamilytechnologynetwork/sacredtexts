| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemma-31b | 27% cov 100% (n=30; c/i/r 8/22/0; minor/major 0/22) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 3/27) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 90% cov 100% (n=30; c/i/r 27/3/0; minor/major 0/3) | **29%** cov 100% (c/i/r 35/85/0; minor/major 3/82) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gemma-31b | cite_passage | 22 | 0 | 22 | wrong_locus 15, no_citation 7 |
| gemma-31b | complete_unit | 30 | 3 | 27 | wrong_passage 27, omission 3 |
| gemma-31b | retrieve_quote | 30 | 0 | 30 | wrong_passage 30 |
| gemma-31b | verify_source | 3 | 0 | 3 | wrong_verdict 3 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemma-31b | Hinduism | 27% cov 100% (n=30; c/i/r 8/22/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 90% cov 100% (n=30; c/i/r 27/3/0) | **29%** cov 100% (n=120; c/i/r 35/85/0) |

### By text (one text = one work · version · language)

**gemma-31b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 29% | 100% | 0 | — | 3 | 82 | wrong_passage 57, omission 3, wrong_locus 15, no_citation 7, wrong_verdict 3 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemma-31b | 120 | 8,715 | 21,031 |
| **total** | 120 | 8,715 | 21,031 |
