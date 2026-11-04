| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| argon | 40% cov 100% (n=30; c/i/r 12/18/0; minor/major 0/18) | 30% cov 100% (n=30; c/i/r 9/21/0; minor/major 9/12) | 3% cov 100% (n=30; c/i/r 1/29/0; minor/major 0/29) | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | **42%** cov 100% (c/i/r 51/69/0; minor/major 9/60) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| argon | cite_passage | 18 | 0 | 18 | wrong_locus 18 |
| argon | complete_unit | 21 | 9 | 12 | edition_variant 3, paraphrase 3, wrong_passage 12, omission 3, addition 2 |
| argon | retrieve_quote | 29 | 0 | 29 | wrong_passage 29, addition 1 |
| argon | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| argon | Judaism | 40% cov 100% (n=30; c/i/r 12/18/0) | 30% cov 100% (n=30; c/i/r 9/21/0) | 3% cov 100% (n=30; c/i/r 1/29/0) | 97% cov 100% (n=30; c/i/r 29/1/0) | **42%** cov 100% (n=120; c/i/r 51/69/0) |

### By text (one text = one work · version · language)

**argon**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 42% | 100% | 0 | — | 9 | 60 | edition_variant 3, paraphrase 3, wrong_passage 41, omission 3, addition 3, wrong_locus 18, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| argon | 120 | 14,697 | 23,068 |
| **total** | 120 | 14,697 | 23,068 |
