| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| beam | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 80% cov 100% (n=30; c/i/r 24/6/0; minor/major 6/0) | 60% cov 100% (n=30; c/i/r 18/12/0; minor/major 12/0) | 93% cov 100% (n=30; c/i/r 28/2/0; minor/major 0/2) | **83%** cov 100% (c/i/r 100/20/0; minor/major 18/2) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| beam | complete_unit | 6 | 6 | 0 | edition_variant 2, near_copy 1, paraphrase 3, addition 2 |
| beam | retrieve_quote | 12 | 12 | 0 | edition_variant 5, near_copy 4, paraphrase 2, omission 1 |
| beam | verify_source | 2 | 0 | 2 | wrong_verdict 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| beam | Christianity | 100% cov 100% (n=30; c/i/r 30/0/0) | 80% cov 100% (n=30; c/i/r 24/6/0) | 60% cov 100% (n=30; c/i/r 18/12/0) | 93% cov 100% (n=30; c/i/r 28/2/0) | **83%** cov 100% (n=120; c/i/r 100/20/0) |

### By text (one text = one work · version · language)

**beam**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (NRSV, en) | 120 | 83% | 100% | 0 | — | 18 | 2 | edition_variant 7, near_copy 5, paraphrase 5, omission 1, addition 2, wrong_verdict 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| beam | 120 | 11,680 | 59,107 |
| **total** | 120 | 11,680 | 59,107 |
