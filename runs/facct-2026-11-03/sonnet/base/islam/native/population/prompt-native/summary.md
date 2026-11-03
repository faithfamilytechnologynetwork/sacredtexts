| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sonnet | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 1/0) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 83% cov 100% (n=30; c/i/r 25/5/0; minor/major 0/5) | **95%** cov 100% (c/i/r 114/6/0; minor/major 1/5) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sonnet | complete_unit | 1 | 1 | 0 | omission 1, addition 9 |
| sonnet | retrieve_quote | 0 | 0 | 0 | addition 9 |
| sonnet | verify_source | 5 | 0 | 5 | wrong_verdict 5 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sonnet | Islam | 100% cov 100% (n=30; c/i/r 30/0/0) | 97% cov 100% (n=30; c/i/r 29/1/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | 83% cov 100% (n=30; c/i/r 25/5/0) | **95%** cov 100% (n=120; c/i/r 114/6/0) |

### By text (one text = one work · version · language)

**sonnet**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Qur'an (Uthmani (QUL), ar) | 120 | 95% | 100% | 0 | — | 1 | 5 | omission 1, addition 18, wrong_verdict 5 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sonnet | 120 | 27,421 | 23,243 |
| **total** | 120 | 27,421 | 23,243 |
