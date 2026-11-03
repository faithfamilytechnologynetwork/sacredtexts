| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemini-flash | 87% cov 100% (n=30; c/i/r 26/4/0; minor/major 0/4) | 75% cov 93% (n=30; c/i/r 21/7/2; minor/major 4/3) | 61% cov 93% (n=30; c/i/r 17/11/2; minor/major 3/8) | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | **80%** cov 97% (c/i/r 93/23/4; minor/major 7/16) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gemini-flash | cite_passage | 4 | 0 | 4 | wrong_locus 4 |
| gemini-flash | complete_unit | 7 | 4 | 3 | edition_variant 2, paraphrase 1, wrong_passage 3, omission 1 |
| gemini-flash | retrieve_quote | 11 | 3 | 8 | edition_variant 2, wrong_passage 8, omission 1, addition 1 |
| gemini-flash | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemini-flash | Book of Mormon | 87% cov 100% (n=30; c/i/r 26/4/0) | 75% cov 93% (n=30; c/i/r 21/7/2) | 61% cov 93% (n=30; c/i/r 17/11/2) | 97% cov 100% (n=30; c/i/r 29/1/0) | **80%** cov 97% (n=120; c/i/r 93/23/4) |

### By text (one text = one work · version · language)

**gemini-flash**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Book of Mormon (2013 edition, en) | 120 | 80% | 97% | 4 | — | 7 | 16 | edition_variant 4, paraphrase 1, wrong_passage 11, omission 2, addition 1, wrong_locus 4, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemini-flash | 120 | 8,870 | 31,113 |
| **total** | 120 | 8,870 | 31,113 |
