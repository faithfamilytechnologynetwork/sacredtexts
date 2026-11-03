| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| luna | 95% cov 100% (n=21; c/i/r 20/1/0; minor/major 0/1) | 19% cov 100% (n=21; c/i/r 4/17/0; minor/major 8/9) | 52% cov 100% (n=21; c/i/r 11/10/0; minor/major 10/0) | 62% cov 100% (n=21; c/i/r 13/8/0; minor/major 0/8) | **57%** cov 100% (c/i/r 48/36/0; minor/major 18/18) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| luna | cite_passage | 1 | 0 | 1 | wrong_locus 1 |
| luna | complete_unit | 17 | 8 | 9 | paraphrase 7, wrong_passage 9, omission 1 |
| luna | retrieve_quote | 10 | 10 | 0 | diacritic_only 1, edition_variant 5, paraphrase 4 |
| luna | verify_source | 8 | 0 | 8 | wrong_verdict 8 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| luna | Christianity | 95% cov 100% (n=21; c/i/r 20/1/0) | 19% cov 100% (n=21; c/i/r 4/17/0) | 52% cov 100% (n=21; c/i/r 11/10/0) | 62% cov 100% (n=21; c/i/r 13/8/0) | **57%** cov 100% (n=84; c/i/r 48/36/0) |

### By text (one text = one work · version · language)

**luna**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 50% | 100% | 0 | — | 1 | 1 | paraphrase 1, wrong_passage 1 |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 57% | 100% | 0 | — | 17 | 17 | diacritic_only 1, edition_variant 5, paraphrase 10, wrong_passage 8, omission 1, wrong_locus 1, wrong_verdict 8 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| luna | 84 | 9,782 | 4,907 |
| **total** | 84 | 9,782 | 4,907 |
