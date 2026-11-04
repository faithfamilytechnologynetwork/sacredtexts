| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| luna | 23% cov 100% (n=30; c/i/r 7/23/0; minor/major 0/23) | 3% cov 100% (n=30; c/i/r 1/29/0; minor/major 7/22) | 7% cov 100% (n=30; c/i/r 2/28/0; minor/major 0/28) | 70% cov 100% (n=30; c/i/r 21/9/0; minor/major 0/9) | **26%** cov 100% (c/i/r 31/89/0; minor/major 7/82) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| luna | cite_passage | 23 | 0 | 23 | wrong_locus 23 |
| luna | complete_unit | 29 | 7 | 22 | edition_variant 1, paraphrase 5, wrong_passage 22, omission 1 |
| luna | retrieve_quote | 28 | 0 | 28 | wrong_passage 27, other_script 1, addition 2 |
| luna | verify_source | 9 | 0 | 9 | wrong_verdict 9 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| luna | Judaism | 23% cov 100% (n=30; c/i/r 7/23/0) | 3% cov 100% (n=30; c/i/r 1/29/0) | 7% cov 100% (n=30; c/i/r 2/28/0) | 70% cov 100% (n=30; c/i/r 21/9/0) | **26%** cov 100% (n=120; c/i/r 31/89/0) |

### By text (one text = one work · version · language)

**luna**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 26% | 100% | 0 | — | 7 | 82 | edition_variant 1, paraphrase 5, wrong_passage 49, other_script 1, omission 1, addition 2, wrong_locus 23, wrong_verdict 9 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| luna | 120 | 11,948 | 18,696 |
| **total** | 120 | 11,948 | 18,696 |
