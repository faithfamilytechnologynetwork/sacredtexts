| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| haiku | 86% cov 97% (n=30; c/i/r 25/4/1; minor/major 0/4) | 41% cov 57% (n=30; c/i/r 7/10/13; minor/major 5/5) | 22% cov 30% (n=30; c/i/r 2/7/21; minor/major 7/0) | 100% cov 87% (n=30; c/i/r 26/0/4; minor/major 0/0) | **74%** cov 68% (c/i/r 60/21/39; minor/major 12/9) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| haiku | cite_passage | 4 | 0 | 4 | wrong_locus 4 |
| haiku | complete_unit | 10 | 5 | 5 | edition_variant 1, near_copy 1, paraphrase 2, wrong_passage 5, omission 1, addition 2 |
| haiku | retrieve_quote | 7 | 7 | 0 | edition_variant 2, near_copy 3, omission 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| haiku | Christianity | 86% cov 97% (n=30; c/i/r 25/4/1) | 41% cov 57% (n=30; c/i/r 7/10/13) | 22% cov 30% (n=30; c/i/r 2/7/21) | 100% cov 87% (n=30; c/i/r 26/0/4) | **74%** cov 68% (n=120; c/i/r 60/21/39) |

### By text (one text = one work · version · language)

**haiku**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (NRSV, en) | 120 | 74% | 68% | 39 | — | 12 | 9 | edition_variant 3, near_copy 4, paraphrase 2, wrong_passage 5, omission 3, addition 2, wrong_locus 4 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| haiku | 120 | 9,707 | 7,824 |
| **total** | 120 | 9,707 | 7,824 |
