| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sol | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 40% cov 17% (n=30; c/i/r 2/3/25; minor/major 0/3) | n/a cov 0% (n=30; c/i/r 0/0/30; minor/major 0/0) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **95%** cov 54% (c/i/r 62/3/55; minor/major 0/3) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sol | complete_unit | 3 | 0 | 3 | wrong_passage 3 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sol | Islam | 100% cov 100% (n=30; c/i/r 30/0/0) | 40% cov 17% (n=30; c/i/r 2/3/25) | n/a cov 0% (n=30; c/i/r 0/0/30) | 100% cov 100% (n=30; c/i/r 30/0/0) | **95%** cov 54% (n=120; c/i/r 62/3/55) |

### By text (one text = one work · version · language)

**sol**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Qur'an (Saheeh International (QUL), en) | 120 | 95% | 54% | 55 | — | 0 | 3 | wrong_passage 3 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sol | 120 | 9,379 | 6,900 |
| **total** | 120 | 9,379 | 6,900 |
