| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| luna | 95% cov 100% (n=21; c/i/r 20/1/0; minor/major 0/1) | 33% cov 100% (n=21; c/i/r 7/14/0; minor/major 7/7) | 57% cov 100% (n=21; c/i/r 12/9/0; minor/major 9/0) | 81% cov 100% (n=21; c/i/r 17/4/0; minor/major 0/4) | **67%** cov 100% (c/i/r 56/28/0; minor/major 16/12) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| luna | cite_passage | 1 | 0 | 1 | wrong_locus 1 |
| luna | complete_unit | 14 | 7 | 7 | edition_variant 1, paraphrase 5, wrong_passage 7, omission 1 |
| luna | retrieve_quote | 9 | 9 | 0 | edition_variant 6, paraphrase 3 |
| luna | verify_source | 4 | 0 | 4 | wrong_verdict 4 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| luna | Christianity | 95% cov 100% (n=21; c/i/r 20/1/0) | 33% cov 100% (n=21; c/i/r 7/14/0) | 57% cov 100% (n=21; c/i/r 12/9/0) | 81% cov 100% (n=21; c/i/r 17/4/0) | **67%** cov 100% (n=84; c/i/r 56/28/0) |

### By text (one text = one work · version · language)

**luna**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 75% | 100% | 0 | — | 0 | 1 | wrong_passage 1 |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 66% | 100% | 0 | — | 16 | 11 | edition_variant 7, paraphrase 8, wrong_passage 6, omission 1, wrong_locus 1, wrong_verdict 4 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| luna | 84 | 11,723 | 4,875 |
| **total** | 84 | 11,723 | 4,875 |
