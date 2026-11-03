| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| opus | 39% cov 93% (n=30; c/i/r 11/17/2; minor/major 0/17) | 16% cov 83% (n=30; c/i/r 4/21/5; minor/major 12/9) | 0% cov 7% (n=30; c/i/r 0/2/28; minor/major 2/0) | 93% cov 100% (n=30; c/i/r 28/2/0; minor/major 0/2) | **51%** cov 71% (c/i/r 43/42/35; minor/major 14/28) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| opus | cite_passage | 17 | 0 | 17 | wrong_locus 14, hedge 3 |
| opus | complete_unit | 21 | 12 | 9 | edition_variant 3, paraphrase 6, wrong_passage 9, omission 3 |
| opus | retrieve_quote | 2 | 2 | 0 | paraphrase 2 |
| opus | verify_source | 2 | 0 | 2 | wrong_verdict 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| opus | Judaism | 39% cov 93% (n=30; c/i/r 11/17/2) | 16% cov 83% (n=30; c/i/r 4/21/5) | 0% cov 7% (n=30; c/i/r 0/2/28) | 93% cov 100% (n=30; c/i/r 28/2/0) | **51%** cov 71% (n=120; c/i/r 43/42/35) |

### By text (one text = one work · version · language)

**opus**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 51% | 71% | 35 | — | 14 | 28 | edition_variant 3, paraphrase 8, wrong_passage 9, omission 3, wrong_locus 14, hedge 3, wrong_verdict 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| opus | 120 | 17,877 | 66,067 |
| **total** | 120 | 17,877 | 66,067 |
