| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemma-31b | 73% cov 100% (n=30; c/i/r 22/8/0; minor/major 0/8) | 3% cov 100% (n=30; c/i/r 1/29/0; minor/major 6/23) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **44%** cov 100% (c/i/r 53/67/0; minor/major 6/61) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gemma-31b | cite_passage | 8 | 0 | 8 | wrong_locus 8 |
| gemma-31b | complete_unit | 29 | 6 | 23 | edition_variant 2, paraphrase 4, wrong_passage 23 |
| gemma-31b | retrieve_quote | 30 | 0 | 30 | wrong_passage 30 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemma-31b | Islam | 73% cov 100% (n=30; c/i/r 22/8/0) | 3% cov 100% (n=30; c/i/r 1/29/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **44%** cov 100% (n=120; c/i/r 53/67/0) |

### By text (one text = one work · version · language)

**gemma-31b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Qur'an (Uthmani (QUL), ar) | 120 | 44% | 100% | 0 | — | 6 | 61 | edition_variant 2, paraphrase 4, wrong_passage 53, wrong_locus 8 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemma-31b | 120 | 16,630 | 4,300 |
| **total** | 120 | 16,630 | 4,300 |
