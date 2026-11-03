| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| kimi | 67% cov 100% (n=30; c/i/r 20/10/0; minor/major 0/10) | 53% cov 100% (n=30; c/i/r 16/14/0; minor/major 10/4) | 61% cov 93% (n=30; c/i/r 17/11/2; minor/major 4/7) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **70%** cov 98% (c/i/r 83/35/2; minor/major 14/21) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| kimi | cite_passage | 10 | 0 | 10 | wrong_locus 10 |
| kimi | complete_unit | 14 | 10 | 4 | edition_variant 4, paraphrase 6, wrong_passage 4, addition 2 |
| kimi | retrieve_quote | 11 | 4 | 7 | edition_variant 2, paraphrase 2, wrong_passage 7 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| kimi | Book of Mormon | 67% cov 100% (n=30; c/i/r 20/10/0) | 53% cov 100% (n=30; c/i/r 16/14/0) | 61% cov 93% (n=30; c/i/r 17/11/2) | 100% cov 100% (n=30; c/i/r 30/0/0) | **70%** cov 98% (n=120; c/i/r 83/35/2) |

### By text (one text = one work · version · language)

**kimi**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Book of Mormon (2013 edition, en) | 120 | 70% | 98% | 2 | — | 14 | 21 | edition_variant 6, paraphrase 8, wrong_passage 11, addition 2, wrong_locus 10 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| kimi | 120 | 10,858 | 7,603 |
| **total** | 120 | 10,858 | 7,603 |
