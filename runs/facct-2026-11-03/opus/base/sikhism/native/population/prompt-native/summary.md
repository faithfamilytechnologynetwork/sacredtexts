| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| opus | 14% cov 70% (n=30; c/i/r 3/18/9; minor/major 0/18) | 20% cov 83% (n=30; c/i/r 5/20/5; minor/major 12/8) | 0% cov 3% (n=30; c/i/r 0/1/29; minor/major 0/1) | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | **48%** cov 64% (c/i/r 37/40/43; minor/major 12/28) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| opus | cite_passage | 18 | 0 | 18 | wrong_locus 13, no_citation 5 |
| opus | complete_unit | 20 | 12 | 8 | edition_variant 3, paraphrase 3, wrong_passage 8, omission 6 |
| opus | retrieve_quote | 1 | 0 | 1 | wrong_passage 1 |
| opus | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| opus | Sikhism | 14% cov 70% (n=30; c/i/r 3/18/9) | 20% cov 83% (n=30; c/i/r 5/20/5) | 0% cov 3% (n=30; c/i/r 0/1/29) | 97% cov 100% (n=30; c/i/r 29/1/0) | **48%** cov 64% (n=120; c/i/r 37/40/43) |

### By text (one text = one work · version · language)

**opus**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 120 | 48% | 64% | 43 | — | 12 | 28 | edition_variant 3, paraphrase 3, wrong_passage 9, omission 6, wrong_locus 13, no_citation 5, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| opus | 120 | 30,418 | 147,535 |
| **total** | 120 | 30,418 | 147,535 |
