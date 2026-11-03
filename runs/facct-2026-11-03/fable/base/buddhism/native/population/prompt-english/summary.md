| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| fable | 93% cov 100% (n=30; c/i/r 28/2/0; minor/major 0/2) | 93% cov 100% (n=30; c/i/r 28/2/0; minor/major 1/1) | 90% cov 100% (n=30; c/i/r 27/3/0; minor/major 3/0) | 100% cov 93% (n=30; c/i/r 28/0/2; minor/major 0/0) | **94%** cov 98% (c/i/r 111/7/2; minor/major 4/3) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| fable | cite_passage | 2 | 0 | 2 | wrong_locus 2 |
| fable | complete_unit | 2 | 1 | 1 | paraphrase 1, wrong_passage 1 |
| fable | retrieve_quote | 3 | 3 | 0 | edition_variant 1, paraphrase 1, omission 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| fable | Buddhism | 93% cov 100% (n=30; c/i/r 28/2/0) | 93% cov 100% (n=30; c/i/r 28/2/0) | 90% cov 100% (n=30; c/i/r 27/3/0) | 100% cov 93% (n=30; c/i/r 28/0/2) | **94%** cov 98% (n=120; c/i/r 111/7/2) |

### By text (one text = one work · version · language)

**fable**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Dhammapada (Chaṭṭha Saṅgāyana (VRI), pi) | 120 | 94% | 98% | 2 | — | 4 | 3 | edition_variant 1, paraphrase 2, wrong_passage 1, omission 1, wrong_locus 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| fable | 120 | 20,794 | 19,107 |
| **total** | 120 | 20,794 | 19,107 |
