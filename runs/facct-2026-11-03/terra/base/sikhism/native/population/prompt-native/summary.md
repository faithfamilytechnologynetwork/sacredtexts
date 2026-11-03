| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| terra | 10% cov 100% (n=30; c/i/r 3/27/0; minor/major 0/27) | 3% cov 100% (n=30; c/i/r 1/29/0; minor/major 2/27) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 80% cov 100% (n=30; c/i/r 24/6/0; minor/major 0/6) | **23%** cov 100% (c/i/r 28/92/0; minor/major 2/90) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| terra | cite_passage | 27 | 0 | 27 | wrong_locus 27 |
| terra | complete_unit | 29 | 2 | 27 | paraphrase 1, wrong_passage 27, omission 1 |
| terra | retrieve_quote | 30 | 0 | 30 | wrong_passage 30 |
| terra | verify_source | 6 | 0 | 6 | wrong_verdict 6 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| terra | Sikhism | 10% cov 100% (n=30; c/i/r 3/27/0) | 3% cov 100% (n=30; c/i/r 1/29/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 80% cov 100% (n=30; c/i/r 24/6/0) | **23%** cov 100% (n=120; c/i/r 28/92/0) |

### By text (one text = one work · version · language)

**terra**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 120 | 23% | 100% | 0 | — | 2 | 90 | paraphrase 1, wrong_passage 57, omission 1, wrong_locus 27, wrong_verdict 6 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| terra | 120 | 10,290 | 2,854 |
| **total** | 120 | 10,290 | 2,854 |
