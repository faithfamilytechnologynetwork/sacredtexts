| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| haiku | 90% cov 100% (n=30; c/i/r 27/3/0; minor/major 0/3) | 70% cov 100% (n=30; c/i/r 21/9/0; minor/major 8/1) | 81% cov 90% (n=30; c/i/r 22/5/3; minor/major 5/0) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **85%** cov 98% (c/i/r 100/17/3; minor/major 13/4) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| haiku | cite_passage | 3 | 0 | 3 | wrong_locus 2, hedge 1 |
| haiku | complete_unit | 9 | 8 | 1 | edition_variant 2, near_copy 1, paraphrase 2, wrong_passage 1, omission 3, addition 5 |
| haiku | retrieve_quote | 5 | 5 | 0 | edition_variant 2, paraphrase 3, addition 3 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| haiku | Islam | 90% cov 100% (n=30; c/i/r 27/3/0) | 70% cov 100% (n=30; c/i/r 21/9/0) | 81% cov 90% (n=30; c/i/r 22/5/3) | 100% cov 100% (n=30; c/i/r 30/0/0) | **85%** cov 98% (n=120; c/i/r 100/17/3) |

### By text (one text = one work · version · language)

**haiku**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Qur'an (Uthmani (QUL), ar) | 120 | 85% | 98% | 3 | — | 13 | 4 | edition_variant 4, near_copy 1, paraphrase 5, wrong_passage 1, omission 3, addition 8, wrong_locus 2, hedge 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| haiku | 120 | 27,784 | 11,713 |
| **total** | 120 | 27,784 | 11,713 |
