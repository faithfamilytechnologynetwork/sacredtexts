| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gpt-oss-20b | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 0% cov 87% (n=30; c/i/r 0/26/4; minor/major 0/26) | n/a cov 0% (n=30; c/i/r 0/0/30; minor/major 0/0) | 50% cov 100% (n=30; c/i/r 15/15/0; minor/major 0/15) | **17%** cov 72% (c/i/r 15/71/34; minor/major 0/71) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gpt-oss-20b | cite_passage | 30 | 0 | 30 | wrong_locus 28, no_citation 2 |
| gpt-oss-20b | complete_unit | 26 | 0 | 26 | wrong_passage 26 |
| gpt-oss-20b | verify_source | 15 | 0 | 15 | wrong_verdict 15 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gpt-oss-20b | Judaism | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 87% (n=30; c/i/r 0/26/4) | n/a cov 0% (n=30; c/i/r 0/0/30) | 50% cov 100% (n=30; c/i/r 15/15/0) | **17%** cov 72% (n=120; c/i/r 15/71/34) |

### By text (one text = one work · version · language)

**gpt-oss-20b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - English, en) | 120 | 17% | 72% | 34 | — | 0 | 71 | wrong_passage 26, wrong_locus 28, no_citation 2, wrong_verdict 15 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gpt-oss-20b | 120 | 20,404 | 144,883 |
| **total** | 120 | 20,404 | 144,883 |
