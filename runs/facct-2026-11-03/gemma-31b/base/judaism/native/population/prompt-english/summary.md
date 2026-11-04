| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemma-31b | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 3/27) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 61% cov 93% (n=30; c/i/r 17/11/2; minor/major 0/11) | **14%** cov 98% (c/i/r 17/101/2; minor/major 3/98) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gemma-31b | cite_passage | 30 | 0 | 30 | wrong_locus 30 |
| gemma-31b | complete_unit | 30 | 3 | 27 | paraphrase 3, wrong_passage 27 |
| gemma-31b | retrieve_quote | 30 | 0 | 30 | wrong_passage 30 |
| gemma-31b | verify_source | 11 | 0 | 11 | wrong_verdict 11 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemma-31b | Judaism | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 61% cov 93% (n=30; c/i/r 17/11/2) | **14%** cov 98% (n=120; c/i/r 17/101/2) |

### By text (one text = one work · version · language)

**gemma-31b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 14% | 98% | 2 | — | 3 | 98 | paraphrase 3, wrong_passage 57, wrong_locus 30, wrong_verdict 11 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemma-31b | 120 | 12,757 | 5,473 |
| **total** | 120 | 12,757 | 5,473 |
