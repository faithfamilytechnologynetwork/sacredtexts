| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| beam | 17% cov 97% (n=30; c/i/r 5/24/1; minor/major 0/24) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 8/22) | 0% cov 10% (n=30; c/i/r 0/3/27; minor/major 0/3) | 87% cov 100% (n=30; c/i/r 26/4/0; minor/major 0/4) | **34%** cov 77% (c/i/r 31/61/28; minor/major 8/53) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| beam | cite_passage | 24 | 0 | 24 | wrong_locus 24 |
| beam | complete_unit | 30 | 8 | 22 | paraphrase 5, wrong_passage 22, omission 3 |
| beam | retrieve_quote | 3 | 0 | 3 | wrong_passage 1, other_script 2 |
| beam | verify_source | 4 | 0 | 4 | wrong_verdict 4 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| beam | Judaism | 17% cov 97% (n=30; c/i/r 5/24/1) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 10% (n=30; c/i/r 0/3/27) | 87% cov 100% (n=30; c/i/r 26/4/0) | **34%** cov 77% (n=120; c/i/r 31/61/28) |

### By text (one text = one work · version · language)

**beam**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 34% | 77% | 28 | — | 8 | 53 | paraphrase 5, wrong_passage 23, other_script 2, omission 3, wrong_locus 24, wrong_verdict 4 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| beam | 120 | 17,792 | 164,461 |
| **total** | 120 | 17,792 | 164,461 |
