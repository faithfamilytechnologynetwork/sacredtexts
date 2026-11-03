| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| astra | 20% cov 100% (n=30; c/i/r 6/24/0; minor/major 0/24) | 5% cov 73% (n=30; c/i/r 1/21/8; minor/major 12/9) | 0% cov 23% (n=30; c/i/r 0/7/23; minor/major 0/7) | 93% cov 100% (n=30; c/i/r 28/2/0; minor/major 0/2) | **39%** cov 74% (c/i/r 35/54/31; minor/major 12/42) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| astra | cite_passage | 24 | 0 | 24 | wrong_locus 24 |
| astra | complete_unit | 21 | 12 | 9 | diacritic_only 1, edition_variant 2, paraphrase 4, wrong_passage 9, omission 5 |
| astra | retrieve_quote | 7 | 0 | 7 | wrong_passage 7 |
| astra | verify_source | 2 | 0 | 2 | wrong_verdict 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| astra | Sikhism | 20% cov 100% (n=30; c/i/r 6/24/0) | 5% cov 73% (n=30; c/i/r 1/21/8) | 0% cov 23% (n=30; c/i/r 0/7/23) | 93% cov 100% (n=30; c/i/r 28/2/0) | **39%** cov 74% (n=120; c/i/r 35/54/31) |

### By text (one text = one work · version · language)

**astra**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 120 | 39% | 74% | 31 | — | 12 | 42 | diacritic_only 1, edition_variant 2, paraphrase 4, wrong_passage 16, omission 5, wrong_locus 24, wrong_verdict 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| astra | 120 | 10,290 | 48,352 |
| **total** | 120 | 10,290 | 48,352 |
