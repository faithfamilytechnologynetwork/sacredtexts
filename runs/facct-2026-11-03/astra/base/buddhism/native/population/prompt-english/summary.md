| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| astra | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 87% cov 100% (n=30; c/i/r 26/4/0; minor/major 2/2) | 83% cov 100% (n=30; c/i/r 25/5/0; minor/major 5/0) | 93% cov 100% (n=30; c/i/r 28/2/0; minor/major 0/2) | **91%** cov 100% (c/i/r 109/11/0; minor/major 7/4) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| astra | complete_unit | 4 | 2 | 2 | paraphrase 2, wrong_passage 2 |
| astra | retrieve_quote | 5 | 5 | 0 | edition_variant 3, paraphrase 1, omission 1 |
| astra | verify_source | 2 | 0 | 2 | wrong_verdict 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| astra | Buddhism | 100% cov 100% (n=30; c/i/r 30/0/0) | 87% cov 100% (n=30; c/i/r 26/4/0) | 83% cov 100% (n=30; c/i/r 25/5/0) | 93% cov 100% (n=30; c/i/r 28/2/0) | **91%** cov 100% (n=120; c/i/r 109/11/0) |

### By text (one text = one work · version · language)

**astra**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Dhammapada (Chaṭṭha Saṅgāyana (VRI), pi) | 120 | 91% | 100% | 0 | — | 7 | 4 | edition_variant 3, paraphrase 3, wrong_passage 2, omission 1, wrong_verdict 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| astra | 120 | 13,878 | 18,189 |
| **total** | 120 | 13,878 | 18,189 |
