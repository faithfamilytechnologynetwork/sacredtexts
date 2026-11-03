| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| haiku | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | 67% cov 100% (n=30; c/i/r 20/10/0; minor/major 9/1) | 67% cov 100% (n=30; c/i/r 20/10/0; minor/major 5/5) | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | **82%** cov 100% (c/i/r 98/22/0; minor/major 14/8) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| haiku | cite_passage | 1 | 0 | 1 | wrong_locus 1 |
| haiku | complete_unit | 10 | 9 | 1 | edition_variant 2, near_copy 2, paraphrase 1, wrong_passage 1, omission 4, addition 4 |
| haiku | retrieve_quote | 10 | 5 | 5 | edition_variant 1, paraphrase 4, wrong_passage 5, addition 9 |
| haiku | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| haiku | Islam | 97% cov 100% (n=30; c/i/r 29/1/0) | 67% cov 100% (n=30; c/i/r 20/10/0) | 67% cov 100% (n=30; c/i/r 20/10/0) | 97% cov 100% (n=30; c/i/r 29/1/0) | **82%** cov 100% (n=120; c/i/r 98/22/0) |

### By text (one text = one work · version · language)

**haiku**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Qur'an (Uthmani (QUL), ar) | 120 | 82% | 100% | 0 | — | 14 | 8 | edition_variant 3, near_copy 2, paraphrase 5, wrong_passage 6, omission 4, addition 13, wrong_locus 1, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| haiku | 120 | 27,181 | 14,033 |
| **total** | 120 | 27,181 | 14,033 |
