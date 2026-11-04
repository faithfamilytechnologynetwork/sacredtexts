| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| fable | 43% cov 100% (n=30; c/i/r 13/17/0; minor/major 0/17) | 43% cov 100% (n=30; c/i/r 13/17/0; minor/major 11/6) | 3% cov 97% (n=30; c/i/r 1/28/1; minor/major 4/24) | 87% cov 77% (n=30; c/i/r 20/3/7; minor/major 0/3) | **42%** cov 93% (c/i/r 47/65/8; minor/major 15/50) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| fable | cite_passage | 17 | 0 | 17 | wrong_locus 16, hedge 1 |
| fable | complete_unit | 17 | 11 | 6 | edition_variant 2, near_copy 1, paraphrase 2, wrong_passage 6, omission 6, addition 2 |
| fable | retrieve_quote | 28 | 4 | 24 | paraphrase 3, wrong_passage 24, omission 1, addition 1 |
| fable | verify_source | 3 | 0 | 3 | wrong_verdict 3 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| fable | Judaism | 43% cov 100% (n=30; c/i/r 13/17/0) | 43% cov 100% (n=30; c/i/r 13/17/0) | 3% cov 97% (n=30; c/i/r 1/28/1) | 87% cov 77% (n=30; c/i/r 20/3/7) | **42%** cov 93% (n=120; c/i/r 47/65/8) |

### By text (one text = one work · version · language)

**fable**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 42% | 93% | 8 | — | 15 | 50 | edition_variant 2, near_copy 1, paraphrase 5, wrong_passage 30, omission 7, addition 3, wrong_locus 16, hedge 1, wrong_verdict 3 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| fable | 120 | 17,875 | 74,345 |
| **total** | 120 | 17,875 | 74,345 |
