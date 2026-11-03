| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| beam | 17% cov 97% (n=30; c/i/r 5/24/1; minor/major 0/24) | 0% cov 97% (n=30; c/i/r 0/29/1; minor/major 5/24) | n/a cov 0% (n=30; c/i/r 0/0/30; minor/major 0/0) | 90% cov 100% (n=30; c/i/r 27/3/0; minor/major 0/3) | **36%** cov 73% (c/i/r 32/56/32; minor/major 5/51) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| beam | cite_passage | 24 | 0 | 24 | wrong_locus 24 |
| beam | complete_unit | 29 | 5 | 24 | edition_variant 1, paraphrase 1, wrong_passage 23, other_script 1, omission 3 |
| beam | verify_source | 3 | 0 | 3 | wrong_verdict 3 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| beam | Judaism | 17% cov 97% (n=30; c/i/r 5/24/1) | 0% cov 97% (n=30; c/i/r 0/29/1) | n/a cov 0% (n=30; c/i/r 0/0/30) | 90% cov 100% (n=30; c/i/r 27/3/0) | **36%** cov 73% (n=120; c/i/r 32/56/32) |

### By text (one text = one work · version · language)

**beam**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 36% | 73% | 32 | — | 5 | 51 | edition_variant 1, paraphrase 1, wrong_passage 23, other_script 1, omission 3, wrong_locus 24, wrong_verdict 3 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| beam | 120 | 18,503 | 171,451 |
| **total** | 120 | 18,503 | 171,451 |
