| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemma-31b | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 1/29) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 80% cov 100% (n=30; c/i/r 24/6/0; minor/major 0/6) | **20%** cov 100% (c/i/r 24/96/0; minor/major 1/95) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gemma-31b | cite_passage | 30 | 0 | 30 | wrong_locus 30 |
| gemma-31b | complete_unit | 30 | 1 | 29 | paraphrase 1, wrong_passage 29 |
| gemma-31b | retrieve_quote | 30 | 0 | 30 | wrong_passage 30 |
| gemma-31b | verify_source | 6 | 0 | 6 | wrong_verdict 6 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemma-31b | Judaism | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 80% cov 100% (n=30; c/i/r 24/6/0) | **20%** cov 100% (n=120; c/i/r 24/96/0) |

### By text (one text = one work · version · language)

**gemma-31b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 20% | 100% | 0 | — | 1 | 95 | paraphrase 1, wrong_passage 59, wrong_locus 30, wrong_verdict 6 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemma-31b | 120 | 12,167 | 7,049 |
| **total** | 120 | 12,167 | 7,049 |
