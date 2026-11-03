| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| kimi | 17% cov 100% (n=30; c/i/r 5/25/0; minor/major 0/25) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 4/26) | 0% cov 90% (n=30; c/i/r 0/27/3; minor/major 0/27) | 77% cov 100% (n=30; c/i/r 23/7/0; minor/major 0/7) | **24%** cov 98% (c/i/r 28/89/3; minor/major 4/85) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| kimi | cite_passage | 25 | 0 | 25 | wrong_locus 25 |
| kimi | complete_unit | 30 | 4 | 26 | paraphrase 3, wrong_passage 26, omission 1 |
| kimi | retrieve_quote | 27 | 0 | 27 | wrong_passage 27 |
| kimi | verify_source | 7 | 0 | 7 | wrong_verdict 7 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| kimi | Judaism | 17% cov 100% (n=30; c/i/r 5/25/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 90% (n=30; c/i/r 0/27/3) | 77% cov 100% (n=30; c/i/r 23/7/0) | **24%** cov 98% (n=120; c/i/r 28/89/3) |

### By text (one text = one work · version · language)

**kimi**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 24% | 98% | 3 | — | 4 | 85 | paraphrase 3, wrong_passage 53, omission 1, wrong_locus 25, wrong_verdict 7 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| kimi | 120 | 16,885 | 43,191 |
| **total** | 120 | 16,885 | 43,191 |
