| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemini-flash | 13% cov 100% (n=30; c/i/r 4/26/0; minor/major 0/26) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 2/28) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **28%** cov 100% (c/i/r 34/86/0; minor/major 2/84) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gemini-flash | cite_passage | 26 | 0 | 26 | wrong_locus 25, no_citation 1 |
| gemini-flash | complete_unit | 30 | 2 | 28 | paraphrase 1, wrong_passage 28, omission 1 |
| gemini-flash | retrieve_quote | 30 | 0 | 30 | wrong_passage 30 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemini-flash | Sikhism | 13% cov 100% (n=30; c/i/r 4/26/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **28%** cov 100% (n=120; c/i/r 34/86/0) |

### By text (one text = one work · version · language)

**gemini-flash**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 120 | 28% | 100% | 0 | — | 2 | 84 | paraphrase 1, wrong_passage 58, omission 1, wrong_locus 25, no_citation 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemini-flash | 120 | 9,843 | 28,184 |
| **total** | 120 | 9,843 | 28,184 |
