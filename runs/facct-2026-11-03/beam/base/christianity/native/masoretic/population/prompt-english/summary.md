| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| beam | 95% cov 100% (n=21; c/i/r 20/1/0; minor/major 0/1) | 60% cov 100% (n=20; c/i/r 12/8/0; minor/major 8/0) | 52% cov 100% (n=21; c/i/r 11/10/0; minor/major 10/0) | 100% cov 100% (n=21; c/i/r 21/0/0; minor/major 0/0) | **77%** cov 100% (c/i/r 64/19/0; minor/major 18/1) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| beam | cite_passage | 1 | 0 | 1 | wrong_locus 1 |
| beam | complete_unit | 8 | 8 | 0 | edition_variant 5, paraphrase 2, omission 1 |
| beam | retrieve_quote | 10 | 10 | 0 | edition_variant 8, paraphrase 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| beam | Christianity | 95% cov 100% (n=21; c/i/r 20/1/0) | 60% cov 100% (n=20; c/i/r 12/8/0) | 52% cov 100% (n=21; c/i/r 11/10/0) | 100% cov 100% (n=21; c/i/r 21/0/0) | **77%** cov 100% (n=83; c/i/r 64/19/0) |

### By text (one text = one work · version · language)

**beam**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 75% | 100% | 0 | — | 1 | 0 | paraphrase 1 |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 79 | 77% | 100% | 0 | — | 17 | 1 | edition_variant 13, paraphrase 3, omission 1, wrong_locus 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| beam | 83 | 17,086 | 116,964 |
| **total** | 83 | 17,086 | 116,964 |
