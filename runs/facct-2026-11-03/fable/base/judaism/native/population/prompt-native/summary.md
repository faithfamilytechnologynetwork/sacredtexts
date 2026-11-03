| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| fable | 27% cov 100% (n=30; c/i/r 8/22/0; minor/major 0/22) | 20% cov 100% (n=30; c/i/r 6/24/0; minor/major 17/7) | 5% cov 63% (n=30; c/i/r 1/18/11; minor/major 3/15) | 96% cov 77% (n=30; c/i/r 22/1/7; minor/major 0/1) | **36%** cov 85% (c/i/r 37/65/18; minor/major 20/45) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| fable | cite_passage | 22 | 0 | 22 | wrong_locus 9, hedge 13 |
| fable | complete_unit | 24 | 17 | 7 | edition_variant 3, near_copy 2, paraphrase 6, wrong_passage 7, omission 6, addition 2 |
| fable | retrieve_quote | 18 | 3 | 15 | near_copy 1, paraphrase 2, wrong_passage 15, addition 1 |
| fable | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| fable | Judaism | 27% cov 100% (n=30; c/i/r 8/22/0) | 20% cov 100% (n=30; c/i/r 6/24/0) | 5% cov 63% (n=30; c/i/r 1/18/11) | 96% cov 77% (n=30; c/i/r 22/1/7) | **36%** cov 85% (n=120; c/i/r 37/65/18) |

### By text (one text = one work · version · language)

**fable**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 36% | 85% | 18 | — | 20 | 45 | edition_variant 3, near_copy 3, paraphrase 8, wrong_passage 22, omission 6, addition 3, wrong_locus 9, hedge 13, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| fable | 120 | 17,877 | 85,074 |
| **total** | 120 | 17,877 | 85,074 |
