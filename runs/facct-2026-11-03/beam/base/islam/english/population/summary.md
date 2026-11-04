| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| beam | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 70% cov 100% (n=30; c/i/r 21/9/0; minor/major 9/0) | 65% cov 87% (n=30; c/i/r 17/9/4; minor/major 9/0) | 90% cov 100% (n=30; c/i/r 27/3/0; minor/major 0/3) | **82%** cov 97% (c/i/r 95/21/4; minor/major 18/3) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| beam | complete_unit | 9 | 9 | 0 | edition_variant 5, near_copy 3, paraphrase 1 |
| beam | retrieve_quote | 9 | 9 | 0 | edition_variant 2, near_copy 7 |
| beam | verify_source | 3 | 0 | 3 | wrong_verdict 3 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| beam | Islam | 100% cov 100% (n=30; c/i/r 30/0/0) | 70% cov 100% (n=30; c/i/r 21/9/0) | 65% cov 87% (n=30; c/i/r 17/9/4) | 90% cov 100% (n=30; c/i/r 27/3/0) | **82%** cov 97% (n=120; c/i/r 95/21/4) |

### By text (one text = one work · version · language)

**beam**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Qur'an (Saheeh International (QUL), en) | 120 | 82% | 97% | 4 | — | 18 | 3 | edition_variant 7, near_copy 10, paraphrase 1, wrong_verdict 3 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| beam | 120 | 14,223 | 68,524 |
| **total** | 120 | 14,223 | 68,524 |
