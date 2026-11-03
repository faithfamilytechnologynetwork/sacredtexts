| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| opus | 41% cov 97% (n=30; c/i/r 12/17/1; minor/major 0/17) | 0% cov 77% (n=30; c/i/r 0/23/7; minor/major 13/10) | n/a cov 0% (n=30; c/i/r 0/0/30; minor/major 0/0) | 73% cov 100% (n=30; c/i/r 22/8/0; minor/major 0/8) | **41%** cov 68% (c/i/r 34/48/38; minor/major 13/35) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| opus | cite_passage | 17 | 0 | 17 | wrong_locus 16, hedge 1 |
| opus | complete_unit | 23 | 13 | 10 | near_copy 1, paraphrase 10, wrong_passage 10, omission 2 |
| opus | verify_source | 8 | 0 | 8 | wrong_verdict 8 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| opus | Judaism | 41% cov 97% (n=30; c/i/r 12/17/1) | 0% cov 77% (n=30; c/i/r 0/23/7) | n/a cov 0% (n=30; c/i/r 0/0/30) | 73% cov 100% (n=30; c/i/r 22/8/0) | **41%** cov 68% (n=120; c/i/r 34/48/38) |

### By text (one text = one work · version · language)

**opus**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - English, en) | 120 | 41% | 68% | 38 | — | 13 | 35 | near_copy 1, paraphrase 10, wrong_passage 10, omission 2, wrong_locus 16, hedge 1, wrong_verdict 8 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| opus | 120 | 18,967 | 53,055 |
| **total** | 120 | 18,967 | 53,055 |
