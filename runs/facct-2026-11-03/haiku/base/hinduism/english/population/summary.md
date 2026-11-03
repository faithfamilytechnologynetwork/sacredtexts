| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| haiku | 100% cov 87% (n=30; c/i/r 26/0/4; minor/major 0/0) | 0% cov 13% (n=30; c/i/r 0/4/26; minor/major 0/4) | n/a cov 0% (n=30; c/i/r 0/0/30; minor/major 0/0) | 81% cov 70% (n=30; c/i/r 17/4/9; minor/major 0/4) | **84%** cov 42% (c/i/r 43/8/69; minor/major 0/8) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| haiku | complete_unit | 4 | 0 | 4 | wrong_passage 4 |
| haiku | verify_source | 4 | 0 | 4 | wrong_verdict 4 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| haiku | Hinduism | 100% cov 87% (n=30; c/i/r 26/0/4) | 0% cov 13% (n=30; c/i/r 0/4/26) | n/a cov 0% (n=30; c/i/r 0/0/30) | 81% cov 70% (n=30; c/i/r 17/4/9) | **84%** cov 42% (n=120; c/i/r 43/8/69) |

### By text (one text = one work · version · language)

**haiku**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Annie Besant (1922), en) | 120 | 84% | 42% | 69 | — | 0 | 8 | wrong_passage 4, wrong_verdict 4 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| haiku | 120 | 11,339 | 16,590 |
| **total** | 120 | 11,339 | 16,590 |
