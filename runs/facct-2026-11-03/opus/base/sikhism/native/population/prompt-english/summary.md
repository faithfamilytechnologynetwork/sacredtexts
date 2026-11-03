| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| opus | 18% cov 93% (n=30; c/i/r 5/23/2; minor/major 0/23) | 17% cov 100% (n=30; c/i/r 5/25/0; minor/major 17/8) | n/a cov 0% (n=30; c/i/r 0/0/30; minor/major 0/0) | 83% cov 100% (n=30; c/i/r 25/5/0; minor/major 0/5) | **40%** cov 73% (c/i/r 35/53/32; minor/major 17/36) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| opus | cite_passage | 23 | 0 | 23 | wrong_locus 22, hedge 1 |
| opus | complete_unit | 25 | 17 | 8 | edition_variant 3, paraphrase 6, wrong_passage 8, omission 8 |
| opus | verify_source | 5 | 0 | 5 | wrong_verdict 5 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| opus | Sikhism | 18% cov 93% (n=30; c/i/r 5/23/2) | 17% cov 100% (n=30; c/i/r 5/25/0) | n/a cov 0% (n=30; c/i/r 0/0/30) | 83% cov 100% (n=30; c/i/r 25/5/0) | **40%** cov 73% (n=120; c/i/r 35/53/32) |

### By text (one text = one work · version · language)

**opus**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 120 | 40% | 73% | 32 | — | 17 | 36 | edition_variant 3, paraphrase 6, wrong_passage 8, omission 8, wrong_locus 22, hedge 1, wrong_verdict 5 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| opus | 120 | 25,667 | 93,098 |
| **total** | 120 | 25,667 | 93,098 |
