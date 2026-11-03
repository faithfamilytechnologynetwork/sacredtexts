| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| kimi | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 87% cov 100% (n=30; c/i/r 26/4/0; minor/major 3/1) | 60% cov 100% (n=30; c/i/r 18/12/0; minor/major 4/8) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **87%** cov 100% (c/i/r 104/16/0; minor/major 7/9) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| kimi | complete_unit | 4 | 3 | 1 | edition_variant 2, paraphrase 1, wrong_passage 1 |
| kimi | retrieve_quote | 12 | 4 | 8 | edition_variant 1, paraphrase 3, wrong_passage 8 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| kimi | Islam | 100% cov 100% (n=30; c/i/r 30/0/0) | 87% cov 100% (n=30; c/i/r 26/4/0) | 60% cov 100% (n=30; c/i/r 18/12/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **87%** cov 100% (n=120; c/i/r 104/16/0) |

### By text (one text = one work · version · language)

**kimi**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Qur'an (Uthmani (QUL), ar) | 120 | 87% | 100% | 0 | — | 7 | 9 | edition_variant 3, paraphrase 4, wrong_passage 9 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| kimi | 120 | 23,599 | 14,532 |
| **total** | 120 | 23,599 | 14,532 |
