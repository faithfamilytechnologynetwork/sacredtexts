| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| kimi | 17% cov 100% (n=30; c/i/r 5/25/0; minor/major 0/25) | 7% cov 100% (n=30; c/i/r 2/28/0; minor/major 5/23) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 90% cov 100% (n=30; c/i/r 27/3/0; minor/major 0/3) | **28%** cov 100% (c/i/r 34/86/0; minor/major 5/81) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| kimi | cite_passage | 25 | 0 | 25 | wrong_locus 24, no_citation 1 |
| kimi | complete_unit | 28 | 5 | 23 | edition_variant 1, paraphrase 3, wrong_passage 23, omission 1 |
| kimi | retrieve_quote | 30 | 0 | 30 | wrong_passage 30 |
| kimi | verify_source | 3 | 0 | 3 | wrong_verdict 3 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| kimi | Judaism | 17% cov 100% (n=30; c/i/r 5/25/0) | 7% cov 100% (n=30; c/i/r 2/28/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 90% cov 100% (n=30; c/i/r 27/3/0) | **28%** cov 100% (n=120; c/i/r 34/86/0) |

### By text (one text = one work · version · language)

**kimi**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 28% | 100% | 0 | — | 5 | 81 | edition_variant 1, paraphrase 3, wrong_passage 53, omission 1, wrong_locus 24, no_citation 1, wrong_verdict 3 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| kimi | 120 | 15,794 | 54,432 |
| **total** | 120 | 15,794 | 54,432 |
