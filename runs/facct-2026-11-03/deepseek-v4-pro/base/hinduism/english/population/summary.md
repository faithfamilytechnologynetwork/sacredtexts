| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| deepseek-v4-pro | 70% cov 100% (n=30; c/i/r 21/9/0; minor/major 0/9) | 10% cov 100% (n=30; c/i/r 3/27/0; minor/major 12/15) | 0% cov 93% (n=30; c/i/r 0/28/2; minor/major 13/15) | 80% cov 100% (n=30; c/i/r 24/6/0; minor/major 0/6) | **41%** cov 98% (c/i/r 48/70/2; minor/major 25/45) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| deepseek-v4-pro | cite_passage | 9 | 0 | 9 | wrong_locus 9 |
| deepseek-v4-pro | complete_unit | 27 | 12 | 15 | edition_variant 1, paraphrase 10, wrong_passage 15, omission 1 |
| deepseek-v4-pro | retrieve_quote | 28 | 13 | 15 | near_copy 1, paraphrase 12, wrong_passage 15 |
| deepseek-v4-pro | verify_source | 6 | 0 | 6 | wrong_verdict 6 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| deepseek-v4-pro | Hinduism | 70% cov 100% (n=30; c/i/r 21/9/0) | 10% cov 100% (n=30; c/i/r 3/27/0) | 0% cov 93% (n=30; c/i/r 0/28/2) | 80% cov 100% (n=30; c/i/r 24/6/0) | **41%** cov 98% (n=120; c/i/r 48/70/2) |

### By text (one text = one work · version · language)

**deepseek-v4-pro**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Annie Besant (1922), en) | 120 | 41% | 98% | 2 | — | 25 | 45 | edition_variant 1, near_copy 1, paraphrase 22, wrong_passage 30, omission 1, wrong_locus 9, wrong_verdict 6 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| deepseek-v4-pro | 120 | 7,689 | 1,757 |
| **total** | 120 | 7,689 | 1,757 |
