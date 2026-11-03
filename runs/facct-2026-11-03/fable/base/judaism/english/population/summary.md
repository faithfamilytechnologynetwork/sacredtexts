| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| fable | 53% cov 100% (n=30; c/i/r 16/14/0; minor/major 0/14) | 3% cov 100% (n=30; c/i/r 1/29/0; minor/major 18/11) | 0% cov 37% (n=30; c/i/r 0/11/19; minor/major 3/8) | 93% cov 90% (n=30; c/i/r 25/2/3; minor/major 0/2) | **43%** cov 82% (c/i/r 42/56/22; minor/major 21/35) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| fable | cite_passage | 14 | 0 | 14 | wrong_locus 13, hedge 1 |
| fable | complete_unit | 29 | 18 | 11 | paraphrase 15, wrong_passage 11, omission 3 |
| fable | retrieve_quote | 11 | 3 | 8 | near_copy 2, paraphrase 1, wrong_passage 8 |
| fable | verify_source | 2 | 0 | 2 | wrong_verdict 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| fable | Judaism | 53% cov 100% (n=30; c/i/r 16/14/0) | 3% cov 100% (n=30; c/i/r 1/29/0) | 0% cov 37% (n=30; c/i/r 0/11/19) | 93% cov 90% (n=30; c/i/r 25/2/3) | **43%** cov 82% (n=120; c/i/r 42/56/22) |

### By text (one text = one work · version · language)

**fable**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - English, en) | 120 | 43% | 82% | 22 | — | 21 | 35 | near_copy 2, paraphrase 16, wrong_passage 19, omission 3, wrong_locus 13, hedge 1, wrong_verdict 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| fable | 120 | 18,967 | 50,581 |
| **total** | 120 | 18,967 | 50,581 |
