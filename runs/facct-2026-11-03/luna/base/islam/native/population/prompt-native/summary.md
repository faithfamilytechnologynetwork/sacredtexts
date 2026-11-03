| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| luna | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 87% cov 100% (n=30; c/i/r 26/4/0; minor/major 3/1) | 43% cov 100% (n=30; c/i/r 13/17/0; minor/major 0/17) | 80% cov 100% (n=30; c/i/r 24/6/0; minor/major 0/6) | **78%** cov 100% (c/i/r 93/27/0; minor/major 3/24) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| luna | complete_unit | 4 | 3 | 1 | edition_variant 3, wrong_passage 1, addition 1 |
| luna | retrieve_quote | 17 | 0 | 17 | wrong_passage 17 |
| luna | verify_source | 6 | 0 | 6 | wrong_verdict 6 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| luna | Islam | 100% cov 100% (n=30; c/i/r 30/0/0) | 87% cov 100% (n=30; c/i/r 26/4/0) | 43% cov 100% (n=30; c/i/r 13/17/0) | 80% cov 100% (n=30; c/i/r 24/6/0) | **78%** cov 100% (n=120; c/i/r 93/27/0) |

### By text (one text = one work · version · language)

**luna**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Qur'an (Uthmani (QUL), ar) | 120 | 78% | 100% | 0 | — | 3 | 24 | edition_variant 3, wrong_passage 18, addition 1, wrong_verdict 6 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| luna | 120 | 17,092 | 6,796 |
| **total** | 120 | 17,092 | 6,796 |
