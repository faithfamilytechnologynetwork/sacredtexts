| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| fable | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 93% cov 100% (n=30; c/i/r 28/2/0; minor/major 1/1) | 83% cov 100% (n=30; c/i/r 25/5/0; minor/major 5/0) | 100% cov 93% (n=30; c/i/r 28/0/2; minor/major 0/0) | **94%** cov 98% (c/i/r 111/7/2; minor/major 6/1) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| fable | complete_unit | 2 | 1 | 1 | edition_variant 1, wrong_passage 1 |
| fable | retrieve_quote | 5 | 5 | 0 | edition_variant 1, near_copy 4 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| fable | Islam | 100% cov 100% (n=30; c/i/r 30/0/0) | 93% cov 100% (n=30; c/i/r 28/2/0) | 83% cov 100% (n=30; c/i/r 25/5/0) | 100% cov 93% (n=30; c/i/r 28/0/2) | **94%** cov 98% (n=120; c/i/r 111/7/2) |

### By text (one text = one work · version · language)

**fable**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Qur'an (Saheeh International (QUL), en) | 120 | 94% | 98% | 2 | — | 6 | 1 | edition_variant 2, near_copy 4, wrong_passage 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| fable | 120 | 13,133 | 12,544 |
| **total** | 120 | 13,133 | 12,544 |
