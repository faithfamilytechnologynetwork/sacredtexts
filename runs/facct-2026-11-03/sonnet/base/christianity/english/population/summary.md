| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sonnet | 90% cov 100% (n=30; c/i/r 27/3/0; minor/major 0/3) | 73% cov 100% (n=30; c/i/r 22/8/0; minor/major 7/1) | 83% cov 60% (n=30; c/i/r 15/3/12; minor/major 3/0) | 79% cov 80% (n=30; c/i/r 19/5/6; minor/major 0/5) | **81%** cov 85% (c/i/r 83/19/18; minor/major 10/9) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sonnet | cite_passage | 3 | 0 | 3 | hedge 3 |
| sonnet | complete_unit | 8 | 7 | 1 | paraphrase 7, wrong_passage 1, addition 18 |
| sonnet | retrieve_quote | 3 | 3 | 0 | edition_variant 1, near_copy 1, paraphrase 1, addition 10 |
| sonnet | verify_source | 5 | 0 | 5 | wrong_verdict 5 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sonnet | Christianity | 90% cov 100% (n=30; c/i/r 27/3/0) | 73% cov 100% (n=30; c/i/r 22/8/0) | 83% cov 60% (n=30; c/i/r 15/3/12) | 79% cov 80% (n=30; c/i/r 19/5/6) | **81%** cov 85% (n=120; c/i/r 83/19/18) |

### By text (one text = one work · version · language)

**sonnet**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (NRSV, en) | 120 | 81% | 85% | 18 | — | 10 | 9 | edition_variant 1, near_copy 1, paraphrase 8, wrong_passage 1, addition 28, hedge 3, wrong_verdict 5 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sonnet | 120 | 9,947 | 13,393 |
| **total** | 120 | 9,947 | 13,393 |
