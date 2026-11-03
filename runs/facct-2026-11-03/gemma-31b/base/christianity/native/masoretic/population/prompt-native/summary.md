| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemma-31b | 14% cov 100% (n=21; c/i/r 3/18/0; minor/major 0/18) | 0% cov 100% (n=21; c/i/r 0/21/0; minor/major 1/20) | 0% cov 100% (n=21; c/i/r 0/21/0; minor/major 0/21) | 100% cov 100% (n=21; c/i/r 21/0/0; minor/major 0/0) | **29%** cov 100% (c/i/r 24/60/0; minor/major 1/59) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gemma-31b | cite_passage | 18 | 0 | 18 | wrong_locus 18 |
| gemma-31b | complete_unit | 21 | 1 | 20 | wrong_passage 20, omission 1 |
| gemma-31b | retrieve_quote | 21 | 0 | 21 | wrong_passage 21 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemma-31b | Christianity | 14% cov 100% (n=21; c/i/r 3/18/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 100% cov 100% (n=21; c/i/r 21/0/0) | **29%** cov 100% (n=84; c/i/r 24/60/0) |

### By text (one text = one work · version · language)

**gemma-31b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 25% | 100% | 0 | — | 0 | 3 | wrong_passage 2, wrong_locus 1 |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 29% | 100% | 0 | — | 1 | 56 | wrong_passage 39, omission 1, wrong_locus 17 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemma-31b | 84 | 9,981 | 10,854 |
| **total** | 84 | 9,981 | 10,854 |
