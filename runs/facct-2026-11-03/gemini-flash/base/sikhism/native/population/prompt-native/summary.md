| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemini-flash | 10% cov 100% (n=30; c/i/r 3/27/0; minor/major 0/27) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 2/28) | 0% cov 100% (n=25; c/i/r 0/25/0; minor/major 0/25) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **29%** cov 100% (c/i/r 33/82/0; minor/major 2/80) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gemini-flash | cite_passage | 27 | 0 | 27 | wrong_locus 27 |
| gemini-flash | complete_unit | 30 | 2 | 28 | paraphrase 1, wrong_passage 28, omission 1 |
| gemini-flash | retrieve_quote | 25 | 0 | 25 | wrong_passage 25 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemini-flash | Sikhism | 10% cov 100% (n=30; c/i/r 3/27/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=25; c/i/r 0/25/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **29%** cov 100% (n=115; c/i/r 33/82/0) |

### By text (one text = one work · version · language)

**gemini-flash**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 115 | 29% | 100% | 0 | — | 2 | 80 | paraphrase 1, wrong_passage 53, omission 1, wrong_locus 27 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemini-flash | 115 | 9,753 | 17,709 |
| **total** | 115 | 9,753 | 17,709 |
