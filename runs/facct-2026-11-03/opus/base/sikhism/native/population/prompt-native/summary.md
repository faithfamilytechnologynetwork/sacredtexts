| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| opus | 13% cov 100% (n=30; c/i/r 4/26/0; minor/major 0/26) | 24% cov 83% (n=30; c/i/r 6/19/5; minor/major 11/8) | 0% cov 8% (n=25; c/i/r 0/2/23; minor/major 0/2) | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | **45%** cov 76% (c/i/r 39/48/28; minor/major 11/37) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| opus | cite_passage | 26 | 0 | 26 | wrong_locus 25, hedge 1 |
| opus | complete_unit | 19 | 11 | 8 | edition_variant 2, paraphrase 3, wrong_passage 8, omission 6 |
| opus | retrieve_quote | 2 | 0 | 2 | wrong_passage 2 |
| opus | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| opus | Sikhism | 13% cov 100% (n=30; c/i/r 4/26/0) | 24% cov 83% (n=30; c/i/r 6/19/5) | 0% cov 8% (n=25; c/i/r 0/2/23) | 97% cov 100% (n=30; c/i/r 29/1/0) | **45%** cov 76% (n=115; c/i/r 39/48/28) |

### By text (one text = one work · version · language)

**opus**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 115 | 45% | 76% | 28 | — | 11 | 37 | edition_variant 2, paraphrase 3, wrong_passage 10, omission 6, wrong_locus 25, hedge 1, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| opus | 115 | 30,359 | 134,297 |
| **total** | 115 | 30,359 | 134,297 |
