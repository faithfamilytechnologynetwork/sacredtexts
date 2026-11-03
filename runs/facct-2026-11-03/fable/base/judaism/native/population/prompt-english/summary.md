| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| fable | 40% cov 100% (n=30; c/i/r 12/18/0; minor/major 0/18) | 23% cov 100% (n=30; c/i/r 7/23/0; minor/major 19/4) | 4% cov 90% (n=30; c/i/r 1/26/3; minor/major 5/21) | 90% cov 100% (n=30; c/i/r 27/3/0; minor/major 0/3) | **40%** cov 98% (c/i/r 47/70/3; minor/major 24/46) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| fable | cite_passage | 18 | 0 | 18 | wrong_locus 5, no_citation 13 |
| fable | complete_unit | 23 | 19 | 4 | edition_variant 4, near_copy 2, paraphrase 5, wrong_passage 4, omission 8 |
| fable | retrieve_quote | 26 | 5 | 21 | near_copy 2, paraphrase 2, wrong_passage 21, omission 1, addition 1 |
| fable | verify_source | 3 | 0 | 3 | wrong_verdict 3 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| fable | Judaism | 40% cov 100% (n=30; c/i/r 12/18/0) | 23% cov 100% (n=30; c/i/r 7/23/0) | 4% cov 90% (n=30; c/i/r 1/26/3) | 90% cov 100% (n=30; c/i/r 27/3/0) | **40%** cov 98% (n=120; c/i/r 47/70/3) |

### By text (one text = one work · version · language)

**fable**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 40% | 98% | 3 | — | 24 | 46 | edition_variant 4, near_copy 4, paraphrase 7, wrong_passage 25, omission 9, addition 1, wrong_locus 5, no_citation 13, wrong_verdict 3 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| fable | 120 | 19,945 | 86,070 |
| **total** | 120 | 19,945 | 86,070 |
