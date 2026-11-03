| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| terra | 40% cov 100% (n=30; c/i/r 12/18/0; minor/major 0/18) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 10/20) | 0% cov 83% (n=30; c/i/r 0/25/5; minor/major 2/23) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **37%** cov 96% (c/i/r 42/73/5; minor/major 12/61) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| terra | cite_passage | 18 | 0 | 18 | wrong_locus 18 |
| terra | complete_unit | 30 | 10 | 20 | near_copy 1, paraphrase 6, wrong_passage 20, omission 3 |
| terra | retrieve_quote | 25 | 2 | 23 | paraphrase 2, wrong_passage 23 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| terra | Judaism | 40% cov 100% (n=30; c/i/r 12/18/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 83% (n=30; c/i/r 0/25/5) | 100% cov 100% (n=30; c/i/r 30/0/0) | **37%** cov 96% (n=120; c/i/r 42/73/5) |

### By text (one text = one work · version · language)

**terra**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - English, en) | 120 | 37% | 96% | 5 | — | 12 | 61 | near_copy 1, paraphrase 8, wrong_passage 43, omission 3, wrong_locus 18 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| terra | 120 | 13,115 | 5,283 |
| **total** | 120 | 13,115 | 5,283 |
