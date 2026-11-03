| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| opus | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 80% cov 100% (n=30; c/i/r 24/6/0; minor/major 5/1) | 67% cov 100% (n=30; c/i/r 20/10/0; minor/major 10/0) | 93% cov 100% (n=30; c/i/r 28/2/0; minor/major 0/2) | **85%** cov 100% (c/i/r 102/18/0; minor/major 15/3) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| opus | complete_unit | 6 | 5 | 1 | edition_variant 1, near_copy 4, wrong_passage 1 |
| opus | retrieve_quote | 10 | 10 | 0 | edition_variant 4, near_copy 6 |
| opus | verify_source | 2 | 0 | 2 | wrong_verdict 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| opus | Islam | 100% cov 100% (n=30; c/i/r 30/0/0) | 80% cov 100% (n=30; c/i/r 24/6/0) | 67% cov 100% (n=30; c/i/r 20/10/0) | 93% cov 100% (n=30; c/i/r 28/2/0) | **85%** cov 100% (n=120; c/i/r 102/18/0) |

### By text (one text = one work · version · language)

**opus**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Qur'an (Saheeh International (QUL), en) | 120 | 85% | 100% | 0 | — | 15 | 3 | edition_variant 5, near_copy 10, wrong_passage 1, wrong_verdict 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| opus | 120 | 13,133 | 21,872 |
| **total** | 120 | 13,133 | 21,872 |
