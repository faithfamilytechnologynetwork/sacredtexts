| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| luna | 27% cov 100% (n=30; c/i/r 8/22/0; minor/major 0/22) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 8/22) | 0% cov 83% (n=30; c/i/r 0/25/5; minor/major 0/25) | 86% cov 97% (n=30; c/i/r 25/4/1; minor/major 0/4) | **29%** cov 95% (c/i/r 33/81/6; minor/major 8/73) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| luna | cite_passage | 22 | 0 | 22 | wrong_locus 22 |
| luna | complete_unit | 30 | 8 | 22 | edition_variant 1, paraphrase 7, wrong_passage 21, other_script 1 |
| luna | retrieve_quote | 25 | 0 | 25 | wrong_passage 22, other_script 3 |
| luna | verify_source | 4 | 0 | 4 | wrong_verdict 4 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| luna | Judaism | 27% cov 100% (n=30; c/i/r 8/22/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 83% (n=30; c/i/r 0/25/5) | 86% cov 97% (n=30; c/i/r 25/4/1) | **29%** cov 95% (n=120; c/i/r 33/81/6) |

### By text (one text = one work · version · language)

**luna**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 29% | 95% | 6 | — | 8 | 73 | edition_variant 1, paraphrase 7, wrong_passage 43, other_script 4, wrong_locus 22, wrong_verdict 4 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| luna | 120 | 12,908 | 20,686 |
| **total** | 120 | 12,908 | 20,686 |
