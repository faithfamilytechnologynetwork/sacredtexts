| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sonnet | 0% cov 77% (n=30; c/i/r 0/23/7; minor/major 0/23) | 0% cov 53% (n=30; c/i/r 0/16/14; minor/major 0/16) | 0% cov 20% (n=25; c/i/r 0/5/20; minor/major 0/5) | 61% cov 60% (n=30; c/i/r 11/7/12; minor/major 0/7) | **18%** cov 54% (c/i/r 11/51/53; minor/major 0/51) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sonnet | cite_passage | 23 | 0 | 23 | wrong_locus 4, hedge 14, no_citation 5 |
| sonnet | complete_unit | 16 | 0 | 16 | wrong_passage 16 |
| sonnet | retrieve_quote | 5 | 0 | 5 | wrong_passage 5 |
| sonnet | verify_source | 7 | 0 | 7 | wrong_verdict 7 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sonnet | Sikhism | 0% cov 77% (n=30; c/i/r 0/23/7) | 0% cov 53% (n=30; c/i/r 0/16/14) | 0% cov 20% (n=25; c/i/r 0/5/20) | 61% cov 60% (n=30; c/i/r 11/7/12) | **18%** cov 54% (n=115; c/i/r 11/51/53) |

### By text (one text = one work · version · language)

**sonnet**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Sri Guru Granth Sahib (Shabad OS (SGPC Shabadaarth), pa) | 115 | 18% | 54% | 53 | — | 0 | 51 | wrong_passage 21, wrong_locus 4, hedge 14, no_citation 5, wrong_verdict 7 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sonnet | 115 | 25,130 | 44,055 |
| **total** | 115 | 25,130 | 44,055 |
