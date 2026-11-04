| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| argon | 43% cov 100% (n=30; c/i/r 13/17/0; minor/major 0/17) | 30% cov 100% (n=30; c/i/r 9/21/0; minor/major 10/11) | 7% cov 100% (n=30; c/i/r 2/28/0; minor/major 0/28) | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | **44%** cov 100% (c/i/r 53/67/0; minor/major 10/57) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| argon | cite_passage | 17 | 0 | 17 | wrong_locus 17 |
| argon | complete_unit | 21 | 10 | 11 | edition_variant 3, paraphrase 7, wrong_passage 11, addition 3 |
| argon | retrieve_quote | 28 | 0 | 28 | wrong_passage 28, addition 2 |
| argon | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| argon | Judaism | 43% cov 100% (n=30; c/i/r 13/17/0) | 30% cov 100% (n=30; c/i/r 9/21/0) | 7% cov 100% (n=30; c/i/r 2/28/0) | 97% cov 100% (n=30; c/i/r 29/1/0) | **44%** cov 100% (n=120; c/i/r 53/67/0) |

### By text (one text = one work · version · language)

**argon**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 44% | 100% | 0 | — | 10 | 57 | edition_variant 3, paraphrase 7, wrong_passage 39, addition 5, wrong_locus 17, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| argon | 120 | 14,739 | 47,568 |
| **total** | 120 | 14,739 | 47,568 |
