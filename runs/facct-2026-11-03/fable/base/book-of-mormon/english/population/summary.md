| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| fable | 67% cov 100% (n=30; c/i/r 20/10/0; minor/major 0/10) | 77% cov 100% (n=30; c/i/r 23/7/0; minor/major 1/6) | 70% cov 100% (n=30; c/i/r 21/9/0; minor/major 3/6) | 100% cov 90% (n=30; c/i/r 27/0/3; minor/major 0/0) | **78%** cov 98% (c/i/r 91/26/3; minor/major 4/22) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| fable | cite_passage | 10 | 0 | 10 | wrong_locus 2, hedge 8 |
| fable | complete_unit | 7 | 1 | 6 | near_copy 1, wrong_passage 6, addition 4 |
| fable | retrieve_quote | 9 | 3 | 6 | edition_variant 2, paraphrase 1, wrong_passage 6, addition 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| fable | Book of Mormon | 67% cov 100% (n=30; c/i/r 20/10/0) | 77% cov 100% (n=30; c/i/r 23/7/0) | 70% cov 100% (n=30; c/i/r 21/9/0) | 100% cov 90% (n=30; c/i/r 27/0/3) | **78%** cov 98% (n=120; c/i/r 91/26/3) |

### By text (one text = one work · version · language)

**fable**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Book of Mormon (2013 edition, en) | 120 | 78% | 98% | 3 | — | 4 | 22 | edition_variant 2, near_copy 1, paraphrase 1, wrong_passage 12, addition 6, wrong_locus 2, hedge 8 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| fable | 120 | 13,423 | 17,111 |
| **total** | 120 | 13,423 | 17,111 |
