| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| kimi | 23% cov 100% (n=30; c/i/r 7/23/0; minor/major 0/23) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 5/25) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 77% cov 100% (n=30; c/i/r 23/7/0; minor/major 0/7) | **25%** cov 100% (c/i/r 30/90/0; minor/major 5/85) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| kimi | cite_passage | 23 | 0 | 23 | wrong_locus 23 |
| kimi | complete_unit | 30 | 5 | 25 | paraphrase 4, wrong_passage 25, omission 1 |
| kimi | retrieve_quote | 30 | 0 | 30 | wrong_passage 30 |
| kimi | verify_source | 7 | 0 | 7 | wrong_verdict 7 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| kimi | Judaism | 23% cov 100% (n=30; c/i/r 7/23/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 77% cov 100% (n=30; c/i/r 23/7/0) | **25%** cov 100% (n=120; c/i/r 30/90/0) |

### By text (one text = one work · version · language)

**kimi**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 25% | 100% | 0 | — | 5 | 85 | paraphrase 4, wrong_passage 55, omission 1, wrong_locus 23, wrong_verdict 7 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| kimi | 120 | 15,565 | 55,073 |
| **total** | 120 | 15,565 | 55,073 |
