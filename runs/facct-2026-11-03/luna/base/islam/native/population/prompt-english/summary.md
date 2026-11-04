| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| luna | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 90% cov 100% (n=30; c/i/r 27/3/0; minor/major 2/1) | 90% cov 100% (n=30; c/i/r 27/3/0; minor/major 2/1) | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | **94%** cov 100% (c/i/r 113/7/0; minor/major 4/3) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| luna | complete_unit | 3 | 2 | 1 | edition_variant 2, wrong_passage 1 |
| luna | retrieve_quote | 3 | 2 | 1 | paraphrase 1, wrong_passage 1, omission 1 |
| luna | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| luna | Islam | 100% cov 100% (n=30; c/i/r 30/0/0) | 90% cov 100% (n=30; c/i/r 27/3/0) | 90% cov 100% (n=30; c/i/r 27/3/0) | 97% cov 100% (n=30; c/i/r 29/1/0) | **94%** cov 100% (n=120; c/i/r 113/7/0) |

### By text (one text = one work · version · language)

**luna**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Qur'an (Uthmani (QUL), ar) | 120 | 94% | 100% | 0 | — | 4 | 3 | edition_variant 2, paraphrase 1, wrong_passage 2, omission 1, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| luna | 120 | 18,481 | 8,151 |
| **total** | 120 | 18,481 | 8,151 |
