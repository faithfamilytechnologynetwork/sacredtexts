| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sonnet | 32% cov 93% (n=30; c/i/r 9/19/2; minor/major 0/19) | 62% cov 87% (n=30; c/i/r 16/10/4; minor/major 0/10) | 35% cov 57% (n=30; c/i/r 6/11/13; minor/major 0/11) | 78% cov 90% (n=30; c/i/r 21/6/3; minor/major 0/6) | **53%** cov 82% (c/i/r 52/46/22; minor/major 0/46) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sonnet | cite_passage | 19 | 0 | 19 | hedge 19 |
| sonnet | complete_unit | 10 | 0 | 10 | wrong_passage 10, addition 13 |
| sonnet | retrieve_quote | 11 | 0 | 11 | wrong_passage 11, addition 6 |
| sonnet | verify_source | 6 | 0 | 6 | wrong_verdict 6 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sonnet | Book of Mormon | 32% cov 93% (n=30; c/i/r 9/19/2) | 62% cov 87% (n=30; c/i/r 16/10/4) | 35% cov 57% (n=30; c/i/r 6/11/13) | 78% cov 90% (n=30; c/i/r 21/6/3) | **53%** cov 82% (n=120; c/i/r 52/46/22) |

### By text (one text = one work · version · language)

**sonnet**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Book of Mormon (2013 edition, en) | 120 | 53% | 82% | 22 | — | 0 | 46 | wrong_passage 21, addition 19, hedge 19, wrong_verdict 6 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sonnet | 120 | 13,423 | 33,114 |
| **total** | 120 | 13,423 | 33,114 |
