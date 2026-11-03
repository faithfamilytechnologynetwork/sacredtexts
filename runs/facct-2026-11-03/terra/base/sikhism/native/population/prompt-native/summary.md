| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| terra | 17% cov 100% (n=30; c/i/r 5/25/0; minor/major 0/25) | 3% cov 100% (n=30; c/i/r 1/29/0; minor/major 2/27) | 0% cov 84% (n=25; c/i/r 0/21/4; minor/major 0/21) | 80% cov 100% (n=30; c/i/r 24/6/0; minor/major 0/6) | **27%** cov 97% (c/i/r 30/81/4; minor/major 2/79) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| terra | cite_passage | 25 | 0 | 25 | wrong_locus 25 |
| terra | complete_unit | 29 | 2 | 27 | paraphrase 1, wrong_passage 27, omission 1 |
| terra | retrieve_quote | 21 | 0 | 21 | wrong_passage 21 |
| terra | verify_source | 6 | 0 | 6 | wrong_verdict 6 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| terra | Sikhism | 17% cov 100% (n=30; c/i/r 5/25/0) | 3% cov 100% (n=30; c/i/r 1/29/0) | 0% cov 84% (n=25; c/i/r 0/21/4) | 80% cov 100% (n=30; c/i/r 24/6/0) | **27%** cov 97% (n=115; c/i/r 30/81/4) |

### By text (one text = one work · version · language)

**terra**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 115 | 27% | 97% | 4 | — | 2 | 79 | paraphrase 1, wrong_passage 48, omission 1, wrong_locus 25, wrong_verdict 6 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| terra | 115 | 10,191 | 2,155 |
| **total** | 115 | 10,191 | 2,155 |
