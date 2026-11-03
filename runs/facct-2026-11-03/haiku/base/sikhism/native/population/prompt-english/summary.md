| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| haiku | 0% cov 50% (n=30; c/i/r 0/15/15; minor/major 0/15) | 0% cov 80% (n=30; c/i/r 0/24/6; minor/major 1/23) | n/a cov 0% (n=30; c/i/r 0/0/30; minor/major 0/0) | 53% cov 63% (n=30; c/i/r 10/9/11; minor/major 0/9) | **17%** cov 48% (c/i/r 10/48/62; minor/major 1/47) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| haiku | cite_passage | 15 | 0 | 15 | wrong_locus 13, no_citation 2 |
| haiku | complete_unit | 24 | 1 | 23 | paraphrase 1, wrong_passage 23 |
| haiku | verify_source | 9 | 0 | 9 | wrong_verdict 9 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| haiku | Sikhism | 0% cov 50% (n=30; c/i/r 0/15/15) | 0% cov 80% (n=30; c/i/r 0/24/6) | n/a cov 0% (n=30; c/i/r 0/0/30) | 53% cov 63% (n=30; c/i/r 10/9/11) | **17%** cov 48% (n=120; c/i/r 10/48/62) |

### By text (one text = one work · version · language)

**haiku**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 120 | 17% | 48% | 62 | — | 1 | 47 | paraphrase 1, wrong_passage 23, wrong_locus 13, no_citation 2, wrong_verdict 9 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| haiku | 120 | 25,427 | 19,079 |
| **total** | 120 | 25,427 | 19,079 |
