| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| terra | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 87% cov 100% (n=30; c/i/r 26/4/0; minor/major 4/0) | 70% cov 100% (n=30; c/i/r 21/9/0; minor/major 9/0) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **89%** cov 100% (c/i/r 107/13/0; minor/major 13/0) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| terra | complete_unit | 4 | 4 | 0 | edition_variant 1, near_copy 1, paraphrase 1, omission 1 |
| terra | retrieve_quote | 9 | 9 | 0 | edition_variant 2, near_copy 6, paraphrase 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| terra | Islam | 100% cov 100% (n=30; c/i/r 30/0/0) | 87% cov 100% (n=30; c/i/r 26/4/0) | 70% cov 100% (n=30; c/i/r 21/9/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **89%** cov 100% (n=120; c/i/r 107/13/0) |

### By text (one text = one work · version · language)

**terra**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Qur'an (Saheeh International (QUL), en) | 120 | 89% | 100% | 0 | — | 13 | 0 | edition_variant 3, near_copy 7, paraphrase 2, omission 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| terra | 120 | 9,344 | 3,684 |
| **total** | 120 | 9,344 | 3,684 |
