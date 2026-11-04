| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| fable | 23% cov 100% (n=30; c/i/r 7/23/0; minor/major 0/23) | 40% cov 100% (n=30; c/i/r 12/18/0; minor/major 11/7) | 16% cov 63% (n=30; c/i/r 3/16/11; minor/major 3/13) | 92% cov 83% (n=30; c/i/r 23/2/5; minor/major 0/2) | **43%** cov 87% (c/i/r 45/59/16; minor/major 14/45) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| fable | cite_passage | 23 | 0 | 23 | wrong_locus 5, hedge 18 |
| fable | complete_unit | 18 | 11 | 7 | edition_variant 1, near_copy 1, paraphrase 3, wrong_passage 7, omission 6, addition 4 |
| fable | retrieve_quote | 16 | 3 | 13 | paraphrase 3, wrong_passage 13, addition 3 |
| fable | verify_source | 2 | 0 | 2 | wrong_verdict 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| fable | Judaism | 23% cov 100% (n=30; c/i/r 7/23/0) | 40% cov 100% (n=30; c/i/r 12/18/0) | 16% cov 63% (n=30; c/i/r 3/16/11) | 92% cov 83% (n=30; c/i/r 23/2/5) | **43%** cov 87% (n=120; c/i/r 45/59/16) |

### By text (one text = one work · version · language)

**fable**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 43% | 87% | 16 | — | 14 | 45 | edition_variant 1, near_copy 1, paraphrase 6, wrong_passage 20, omission 6, addition 7, wrong_locus 5, hedge 18, wrong_verdict 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| fable | 120 | 16,527 | 83,275 |
| **total** | 120 | 16,527 | 83,275 |
