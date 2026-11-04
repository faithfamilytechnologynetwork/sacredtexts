| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sonnet | 8% cov 83% (n=30; c/i/r 2/23/5; minor/major 0/23) | 3% cov 100% (n=30; c/i/r 1/29/0; minor/major 4/25) | 0% cov 33% (n=30; c/i/r 0/10/20; minor/major 0/10) | 57% cov 100% (n=30; c/i/r 17/13/0; minor/major 0/13) | **21%** cov 79% (c/i/r 20/75/25; minor/major 4/71) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sonnet | cite_passage | 23 | 0 | 23 | wrong_locus 8, hedge 15 |
| sonnet | complete_unit | 29 | 4 | 25 | edition_variant 1, paraphrase 1, wrong_passage 25, omission 2 |
| sonnet | retrieve_quote | 10 | 0 | 10 | wrong_passage 10 |
| sonnet | verify_source | 13 | 0 | 13 | wrong_verdict 13 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sonnet | Judaism | 8% cov 83% (n=30; c/i/r 2/23/5) | 3% cov 100% (n=30; c/i/r 1/29/0) | 0% cov 33% (n=30; c/i/r 0/10/20) | 57% cov 100% (n=30; c/i/r 17/13/0) | **21%** cov 79% (n=120; c/i/r 20/75/25) |

### By text (one text = one work · version · language)

**sonnet**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 21% | 79% | 25 | — | 4 | 71 | edition_variant 1, paraphrase 1, wrong_passage 35, omission 2, wrong_locus 8, hedge 15, wrong_verdict 13 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sonnet | 120 | 16,527 | 59,039 |
| **total** | 120 | 16,527 | 59,039 |
