| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| argon | 40% cov 100% (n=30; c/i/r 12/18/0; minor/major 0/18) | 0% cov 90% (n=30; c/i/r 0/27/3; minor/major 15/12) | n/a cov 0% (n=30; c/i/r 0/0/30; minor/major 0/0) | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | **47%** cov 72% (c/i/r 41/46/33; minor/major 15/31) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| argon | cite_passage | 18 | 0 | 18 | wrong_locus 18 |
| argon | complete_unit | 27 | 15 | 12 | paraphrase 14, wrong_passage 12, omission 1 |
| argon | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| argon | Judaism | 40% cov 100% (n=30; c/i/r 12/18/0) | 0% cov 90% (n=30; c/i/r 0/27/3) | n/a cov 0% (n=30; c/i/r 0/0/30) | 97% cov 100% (n=30; c/i/r 29/1/0) | **47%** cov 72% (n=120; c/i/r 41/46/33) |

### By text (one text = one work · version · language)

**argon**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - English, en) | 120 | 47% | 72% | 33 | — | 15 | 31 | paraphrase 14, wrong_passage 12, omission 1, wrong_locus 18, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| argon | 120 | 16,994 | 5,282 |
| **total** | 120 | 16,994 | 5,282 |
