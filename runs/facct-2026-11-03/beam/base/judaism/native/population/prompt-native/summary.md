| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| beam | 25% cov 93% (n=30; c/i/r 7/21/2; minor/major 0/21) | 0% cov 93% (n=30; c/i/r 0/28/2; minor/major 5/23) | 0% cov 20% (n=30; c/i/r 0/6/24; minor/major 0/6) | 90% cov 100% (n=30; c/i/r 27/3/0; minor/major 0/3) | **37%** cov 77% (c/i/r 34/58/28; minor/major 5/53) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| beam | cite_passage | 21 | 0 | 21 | wrong_locus 21 |
| beam | complete_unit | 28 | 5 | 23 | paraphrase 2, wrong_passage 21, other_script 2, omission 3 |
| beam | retrieve_quote | 6 | 0 | 6 | wrong_passage 4, other_script 2 |
| beam | verify_source | 3 | 0 | 3 | wrong_verdict 3 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| beam | Judaism | 25% cov 93% (n=30; c/i/r 7/21/2) | 0% cov 93% (n=30; c/i/r 0/28/2) | 0% cov 20% (n=30; c/i/r 0/6/24) | 90% cov 100% (n=30; c/i/r 27/3/0) | **37%** cov 77% (n=120; c/i/r 34/58/28) |

### By text (one text = one work · version · language)

**beam**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 37% | 77% | 28 | — | 5 | 53 | paraphrase 2, wrong_passage 25, other_script 4, omission 3, wrong_locus 21, wrong_verdict 3 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| beam | 120 | 16,016 | 141,499 |
| **total** | 120 | 16,016 | 141,499 |
