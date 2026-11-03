| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| kimi | 30% cov 100% (n=30; c/i/r 9/21/0; minor/major 0/21) | 0% cov 97% (n=30; c/i/r 0/29/1; minor/major 15/14) | 0% cov 53% (n=30; c/i/r 0/16/14; minor/major 0/16) | 87% cov 100% (n=30; c/i/r 26/4/0; minor/major 0/4) | **33%** cov 88% (c/i/r 35/70/15; minor/major 15/55) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| kimi | cite_passage | 21 | 0 | 21 | wrong_locus 20, no_citation 1 |
| kimi | complete_unit | 29 | 15 | 14 | paraphrase 15, wrong_passage 14 |
| kimi | retrieve_quote | 16 | 0 | 16 | wrong_passage 16 |
| kimi | verify_source | 4 | 0 | 4 | wrong_verdict 4 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| kimi | Judaism | 30% cov 100% (n=30; c/i/r 9/21/0) | 0% cov 97% (n=30; c/i/r 0/29/1) | 0% cov 53% (n=30; c/i/r 0/16/14) | 87% cov 100% (n=30; c/i/r 26/4/0) | **33%** cov 88% (n=120; c/i/r 35/70/15) |

### By text (one text = one work · version · language)

**kimi**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - English, en) | 120 | 33% | 88% | 15 | — | 15 | 55 | paraphrase 15, wrong_passage 30, wrong_locus 20, no_citation 1, wrong_verdict 4 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| kimi | 120 | 14,681 | 7,790 |
| **total** | 120 | 14,681 | 7,790 |
