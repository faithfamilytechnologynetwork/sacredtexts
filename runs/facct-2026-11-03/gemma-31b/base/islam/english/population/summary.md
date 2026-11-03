| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemma-31b | 57% cov 100% (n=30; c/i/r 17/13/0; minor/major 0/13) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 10/20) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 1/29) | 90% cov 100% (n=30; c/i/r 27/3/0; minor/major 0/3) | **37%** cov 100% (c/i/r 44/76/0; minor/major 11/65) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gemma-31b | cite_passage | 13 | 0 | 13 | wrong_locus 13 |
| gemma-31b | complete_unit | 30 | 10 | 20 | paraphrase 7, wrong_passage 20, omission 3 |
| gemma-31b | retrieve_quote | 30 | 1 | 29 | paraphrase 1, wrong_passage 29 |
| gemma-31b | verify_source | 3 | 0 | 3 | wrong_verdict 3 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemma-31b | Islam | 57% cov 100% (n=30; c/i/r 17/13/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 90% cov 100% (n=30; c/i/r 27/3/0) | **37%** cov 100% (n=120; c/i/r 44/76/0) |

### By text (one text = one work · version · language)

**gemma-31b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Qur'an (Saheeh International (QUL), en) | 120 | 37% | 100% | 0 | — | 11 | 65 | paraphrase 8, wrong_passage 49, omission 3, wrong_locus 13, wrong_verdict 3 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemma-31b | 120 | 10,246 | 1,713 |
| **total** | 120 | 10,246 | 1,713 |
