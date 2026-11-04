| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| argon | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 90% cov 100% (n=30; c/i/r 27/3/0; minor/major 3/0) | 77% cov 100% (n=30; c/i/r 23/7/0; minor/major 7/0) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **92%** cov 100% (c/i/r 110/10/0; minor/major 10/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| argon | complete_unit | 3 | 3 | 0 | edition_variant 1, near_copy 1, omission 1 |
| argon | retrieve_quote | 7 | 7 | 0 | near_copy 7 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| argon | Islam | 100% cov 100% (n=30; c/i/r 30/0/0) | 90% cov 100% (n=30; c/i/r 27/3/0) | 77% cov 100% (n=30; c/i/r 23/7/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **92%** cov 100% (n=120; c/i/r 110/10/0) |

### By text (one text = one work · version · language)

**argon**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Qur'an (Saheeh International (QUL), en) | 120 | 92% | 100% | 0 | — | 10 | 0 | edition_variant 1, near_copy 8, omission 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| argon | 120 | 12,332 | 3,783 |
| **total** | 120 | 12,332 | 3,783 |
