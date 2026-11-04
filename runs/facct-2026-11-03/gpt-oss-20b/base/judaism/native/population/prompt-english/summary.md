| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gpt-oss-20b | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 0% cov 97% (n=30; c/i/r 0/29/1; minor/major 1/28) | 0% cov 43% (n=30; c/i/r 0/13/17; minor/major 0/13) | 50% cov 100% (n=30; c/i/r 15/15/0; minor/major 0/15) | **15%** cov 85% (c/i/r 15/87/18; minor/major 1/86) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gpt-oss-20b | cite_passage | 30 | 0 | 30 | wrong_locus 28, hedge 2 |
| gpt-oss-20b | complete_unit | 29 | 1 | 28 | paraphrase 1, wrong_passage 28 |
| gpt-oss-20b | retrieve_quote | 13 | 0 | 13 | wrong_passage 13 |
| gpt-oss-20b | verify_source | 15 | 0 | 15 | wrong_verdict 15 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gpt-oss-20b | Judaism | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 97% (n=30; c/i/r 0/29/1) | 0% cov 43% (n=30; c/i/r 0/13/17) | 50% cov 100% (n=30; c/i/r 15/15/0) | **15%** cov 85% (n=120; c/i/r 15/87/18) |

### By text (one text = one work · version · language)

**gpt-oss-20b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 15% | 85% | 18 | — | 1 | 86 | paraphrase 1, wrong_passage 41, wrong_locus 28, hedge 2, wrong_verdict 15 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gpt-oss-20b | 120 | 19,241 | 88,003 |
| **total** | 120 | 19,241 | 88,003 |
