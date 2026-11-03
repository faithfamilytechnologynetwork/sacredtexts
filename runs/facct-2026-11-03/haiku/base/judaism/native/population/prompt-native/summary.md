| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| haiku | 20% cov 17% (n=30; c/i/r 1/4/25; minor/major 0/4) | 0% cov 30% (n=30; c/i/r 0/9/21; minor/major 0/9) | n/a cov 0% (n=30; c/i/r 0/0/30; minor/major 0/0) | 60% cov 83% (n=30; c/i/r 15/10/5; minor/major 0/10) | **41%** cov 32% (c/i/r 16/23/81; minor/major 0/23) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| haiku | cite_passage | 4 | 0 | 4 | wrong_locus 4 |
| haiku | complete_unit | 9 | 0 | 9 | wrong_passage 9 |
| haiku | verify_source | 10 | 0 | 10 | wrong_verdict 10 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| haiku | Judaism | 20% cov 17% (n=30; c/i/r 1/4/25) | 0% cov 30% (n=30; c/i/r 0/9/21) | n/a cov 0% (n=30; c/i/r 0/0/30) | 60% cov 83% (n=30; c/i/r 15/10/5) | **41%** cov 32% (n=120; c/i/r 16/23/81) |

### By text (one text = one work · version · language)

**haiku**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 41% | 32% | 81 | — | 0 | 23 | wrong_passage 9, wrong_locus 4, wrong_verdict 10 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| haiku | 120 | 17,637 | 61,040 |
| **total** | 120 | 17,637 | 61,040 |
