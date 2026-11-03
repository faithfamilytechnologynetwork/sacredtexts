| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| deepseek-v4-pro | 57% cov 100% (n=30; c/i/r 17/13/0; minor/major 0/13) | 63% cov 100% (n=30; c/i/r 19/11/0; minor/major 10/1) | 17% cov 100% (n=30; c/i/r 5/25/0; minor/major 5/20) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **59%** cov 100% (c/i/r 71/49/0; minor/major 15/34) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| deepseek-v4-pro | cite_passage | 13 | 0 | 13 | wrong_locus 13 |
| deepseek-v4-pro | complete_unit | 11 | 10 | 1 | edition_variant 1, wrong_passage 1, omission 9 |
| deepseek-v4-pro | retrieve_quote | 25 | 5 | 20 | near_copy 1, paraphrase 2, wrong_passage 20, omission 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| deepseek-v4-pro | Islam | 57% cov 100% (n=30; c/i/r 17/13/0) | 63% cov 100% (n=30; c/i/r 19/11/0) | 17% cov 100% (n=30; c/i/r 5/25/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **59%** cov 100% (n=120; c/i/r 71/49/0) |

### By text (one text = one work · version · language)

**deepseek-v4-pro**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Qur'an (Uthmani (QUL), ar) | 120 | 59% | 100% | 0 | — | 15 | 34 | edition_variant 1, near_copy 1, paraphrase 2, wrong_passage 21, omission 11, wrong_locus 13 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| deepseek-v4-pro | 120 | 16,979 | 5,144 |
| **total** | 120 | 16,979 | 5,144 |
