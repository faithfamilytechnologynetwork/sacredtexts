| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| deepseek-v4-pro | 53% cov 100% (n=30; c/i/r 16/14/0; minor/major 0/14) | 33% cov 100% (n=30; c/i/r 10/20/0; minor/major 14/6) | 33% cov 100% (n=30; c/i/r 10/20/0; minor/major 2/18) | 70% cov 100% (n=30; c/i/r 21/9/0; minor/major 0/9) | **48%** cov 100% (c/i/r 57/63/0; minor/major 16/47) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| deepseek-v4-pro | cite_passage | 14 | 0 | 14 | wrong_locus 14 |
| deepseek-v4-pro | complete_unit | 20 | 14 | 6 | near_copy 1, paraphrase 5, wrong_passage 6, omission 8 |
| deepseek-v4-pro | retrieve_quote | 20 | 2 | 18 | edition_variant 1, paraphrase 1, wrong_passage 18 |
| deepseek-v4-pro | verify_source | 9 | 0 | 9 | wrong_verdict 9 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| deepseek-v4-pro | Book of Mormon | 53% cov 100% (n=30; c/i/r 16/14/0) | 33% cov 100% (n=30; c/i/r 10/20/0) | 33% cov 100% (n=30; c/i/r 10/20/0) | 70% cov 100% (n=30; c/i/r 21/9/0) | **48%** cov 100% (n=120; c/i/r 57/63/0) |

### By text (one text = one work · version · language)

**deepseek-v4-pro**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Book of Mormon (2013 edition, en) | 120 | 48% | 100% | 0 | — | 16 | 47 | edition_variant 1, near_copy 1, paraphrase 6, wrong_passage 24, omission 8, wrong_locus 14, wrong_verdict 9 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| deepseek-v4-pro | 120 | 9,139 | 1,953 |
| **total** | 120 | 9,139 | 1,953 |
