| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| argon | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | 80% cov 100% (n=30; c/i/r 24/6/0; minor/major 3/3) | 63% cov 100% (n=30; c/i/r 19/11/0; minor/major 4/7) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **85%** cov 100% (c/i/r 102/18/0; minor/major 7/11) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| argon | cite_passage | 1 | 0 | 1 | wrong_locus 1 |
| argon | complete_unit | 6 | 3 | 3 | edition_variant 2, paraphrase 1, wrong_passage 3 |
| argon | retrieve_quote | 11 | 4 | 7 | edition_variant 2, paraphrase 2, wrong_passage 7 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| argon | Book of Mormon | 97% cov 100% (n=30; c/i/r 29/1/0) | 80% cov 100% (n=30; c/i/r 24/6/0) | 63% cov 100% (n=30; c/i/r 19/11/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **85%** cov 100% (n=120; c/i/r 102/18/0) |

### By text (one text = one work · version · language)

**argon**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Book of Mormon (2013 edition, en) | 120 | 85% | 100% | 0 | — | 7 | 11 | edition_variant 4, paraphrase 3, wrong_passage 10, wrong_locus 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| argon | 120 | 12,611 | 2,716 |
| **total** | 120 | 12,611 | 2,716 |
