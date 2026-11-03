| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| luna | 27% cov 100% (n=30; c/i/r 8/22/0; minor/major 0/22) | 0% cov 97% (n=30; c/i/r 0/29/1; minor/major 7/22) | n/a cov 0% (n=30; c/i/r 0/0/30; minor/major 0/0) | 80% cov 100% (n=30; c/i/r 24/6/0; minor/major 0/6) | **36%** cov 74% (c/i/r 32/57/31; minor/major 7/50) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| luna | cite_passage | 22 | 0 | 22 | wrong_locus 22 |
| luna | complete_unit | 29 | 7 | 22 | paraphrase 6, wrong_passage 22, omission 1 |
| luna | verify_source | 6 | 0 | 6 | wrong_verdict 6 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| luna | Judaism | 27% cov 100% (n=30; c/i/r 8/22/0) | 0% cov 97% (n=30; c/i/r 0/29/1) | n/a cov 0% (n=30; c/i/r 0/0/30) | 80% cov 100% (n=30; c/i/r 24/6/0) | **36%** cov 74% (n=120; c/i/r 32/57/31) |

### By text (one text = one work · version · language)

**luna**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - English, en) | 120 | 36% | 74% | 31 | — | 7 | 50 | paraphrase 6, wrong_passage 22, omission 1, wrong_locus 22, wrong_verdict 6 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| luna | 120 | 13,115 | 2,714 |
| **total** | 120 | 13,115 | 2,714 |
