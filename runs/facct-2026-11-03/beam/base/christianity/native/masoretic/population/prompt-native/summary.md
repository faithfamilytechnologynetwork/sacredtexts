| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| beam | 100% cov 100% (n=21; c/i/r 21/0/0; minor/major 0/0) | 48% cov 100% (n=21; c/i/r 10/11/0; minor/major 10/1) | 43% cov 100% (n=21; c/i/r 9/12/0; minor/major 12/0) | 90% cov 100% (n=21; c/i/r 19/2/0; minor/major 0/2) | **70%** cov 100% (c/i/r 59/25/0; minor/major 22/3) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| beam | complete_unit | 11 | 10 | 1 | edition_variant 9, paraphrase 1, wrong_passage 1 |
| beam | retrieve_quote | 12 | 12 | 0 | edition_variant 7, paraphrase 5 |
| beam | verify_source | 2 | 0 | 2 | wrong_verdict 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| beam | Christianity | 100% cov 100% (n=21; c/i/r 21/0/0) | 48% cov 100% (n=21; c/i/r 10/11/0) | 43% cov 100% (n=21; c/i/r 9/12/0) | 90% cov 100% (n=21; c/i/r 19/2/0) | **70%** cov 100% (n=84; c/i/r 59/25/0) |

### By text (one text = one work · version · language)

**beam**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 75% | 100% | 0 | — | 1 | 0 | paraphrase 1 |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 70% | 100% | 0 | — | 21 | 3 | edition_variant 16, paraphrase 5, wrong_passage 1, wrong_verdict 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| beam | 84 | 15,264 | 95,877 |
| **total** | 84 | 15,264 | 95,877 |
