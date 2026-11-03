| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gpt-oss-20b | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 0% cov 43% (n=30; c/i/r 0/13/17; minor/major 0/13) | 71% cov 70% (n=30; c/i/r 15/6/9; minor/major 0/6) | **16%** cov 78% (c/i/r 15/79/26; minor/major 0/79) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gpt-oss-20b | cite_passage | 30 | 0 | 30 | wrong_locus 30 |
| gpt-oss-20b | complete_unit | 30 | 0 | 30 | wrong_passage 30 |
| gpt-oss-20b | retrieve_quote | 13 | 0 | 13 | wrong_passage 13 |
| gpt-oss-20b | verify_source | 6 | 0 | 6 | wrong_verdict 6 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gpt-oss-20b | Buddhism | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 43% (n=30; c/i/r 0/13/17) | 71% cov 70% (n=30; c/i/r 15/6/9) | **16%** cov 78% (n=120; c/i/r 15/79/26) |

### By text (one text = one work · version · language)

**gpt-oss-20b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Dhammapada (Chaṭṭha Saṅgāyana (VRI), pi) | 120 | 16% | 78% | 26 | — | 0 | 79 | wrong_passage 43, wrong_locus 30, wrong_verdict 6 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gpt-oss-20b | 120 | 21,188 | 22,979 |
| **total** | 120 | 21,188 | 22,979 |
