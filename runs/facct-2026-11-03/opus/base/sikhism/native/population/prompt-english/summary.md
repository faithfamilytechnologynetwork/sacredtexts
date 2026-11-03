| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| opus | 10% cov 97% (n=30; c/i/r 3/26/1; minor/major 0/26) | 17% cov 100% (n=30; c/i/r 5/25/0; minor/major 17/8) | 0% cov 76% (n=25; c/i/r 0/19/6; minor/major 0/19) | 83% cov 100% (n=30; c/i/r 25/5/0; minor/major 0/5) | **31%** cov 94% (c/i/r 33/75/7; minor/major 17/58) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| opus | cite_passage | 26 | 0 | 26 | wrong_locus 26 |
| opus | complete_unit | 25 | 17 | 8 | edition_variant 3, paraphrase 6, wrong_passage 8, omission 8 |
| opus | retrieve_quote | 19 | 0 | 19 | wrong_passage 19 |
| opus | verify_source | 5 | 0 | 5 | wrong_verdict 5 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| opus | Sikhism | 10% cov 97% (n=30; c/i/r 3/26/1) | 17% cov 100% (n=30; c/i/r 5/25/0) | 0% cov 76% (n=25; c/i/r 0/19/6) | 83% cov 100% (n=30; c/i/r 25/5/0) | **31%** cov 94% (n=115; c/i/r 33/75/7) |

### By text (one text = one work · version · language)

**opus**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 115 | 31% | 94% | 7 | — | 17 | 58 | edition_variant 3, paraphrase 6, wrong_passage 27, omission 8, wrong_locus 26, wrong_verdict 5 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| opus | 115 | 25,130 | 98,480 |
| **total** | 115 | 25,130 | 98,480 |
