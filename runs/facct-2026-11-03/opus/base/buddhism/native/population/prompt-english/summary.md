| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| opus | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 83% cov 100% (n=30; c/i/r 25/5/0; minor/major 3/2) | 83% cov 100% (n=30; c/i/r 25/5/0; minor/major 5/0) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **92%** cov 100% (c/i/r 110/10/0; minor/major 8/2) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| opus | complete_unit | 5 | 3 | 2 | edition_variant 1, paraphrase 2, wrong_passage 2 |
| opus | retrieve_quote | 5 | 5 | 0 | edition_variant 2, near_copy 1, paraphrase 1, omission 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| opus | Buddhism | 100% cov 100% (n=30; c/i/r 30/0/0) | 83% cov 100% (n=30; c/i/r 25/5/0) | 83% cov 100% (n=30; c/i/r 25/5/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **92%** cov 100% (n=120; c/i/r 110/10/0) |

### By text (one text = one work · version · language)

**opus**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Dhammapada (Chaṭṭha Saṅgāyana (VRI), pi) | 120 | 92% | 100% | 0 | — | 8 | 2 | edition_variant 3, near_copy 1, paraphrase 3, wrong_passage 2, omission 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| opus | 120 | 20,794 | 34,164 |
| **total** | 120 | 20,794 | 34,164 |
