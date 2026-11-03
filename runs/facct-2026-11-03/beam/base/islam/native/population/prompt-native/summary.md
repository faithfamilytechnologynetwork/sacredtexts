| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| beam | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 93% cov 100% (n=30; c/i/r 28/2/0; minor/major 2/0) | 63% cov 100% (n=30; c/i/r 19/11/0; minor/major 11/0) | 90% cov 100% (n=30; c/i/r 27/3/0; minor/major 0/3) | **87%** cov 100% (c/i/r 104/16/0; minor/major 13/3) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| beam | complete_unit | 2 | 2 | 0 | edition_variant 2 |
| beam | retrieve_quote | 11 | 11 | 0 | edition_variant 1, near_copy 5, paraphrase 5 |
| beam | verify_source | 3 | 0 | 3 | wrong_verdict 3 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| beam | Islam | 100% cov 100% (n=30; c/i/r 30/0/0) | 93% cov 100% (n=30; c/i/r 28/2/0) | 63% cov 100% (n=30; c/i/r 19/11/0) | 90% cov 100% (n=30; c/i/r 27/3/0) | **87%** cov 100% (n=120; c/i/r 104/16/0) |

### By text (one text = one work · version · language)

**beam**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Qur'an (Uthmani (QUL), ar) | 120 | 87% | 100% | 0 | — | 13 | 3 | edition_variant 3, near_copy 5, paraphrase 5, wrong_verdict 3 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| beam | 120 | 26,299 | 101,636 |
| **total** | 120 | 26,299 | 101,636 |
