| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| haiku | 71% cov 100% (n=21; c/i/r 15/6/0; minor/major 0/6) | 5% cov 100% (n=21; c/i/r 1/20/0; minor/major 4/16) | 14% cov 100% (n=21; c/i/r 3/18/0; minor/major 15/3) | 90% cov 100% (n=21; c/i/r 19/2/0; minor/major 0/2) | **45%** cov 100% (c/i/r 38/46/0; minor/major 19/27) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| haiku | cite_passage | 6 | 0 | 6 | wrong_locus 5, hedge 1 |
| haiku | complete_unit | 20 | 4 | 16 | edition_variant 2, paraphrase 2, wrong_passage 9, other_script 7, addition 1 |
| haiku | retrieve_quote | 18 | 15 | 3 | edition_variant 6, paraphrase 9, wrong_passage 3 |
| haiku | verify_source | 2 | 0 | 2 | wrong_verdict 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| haiku | Christianity | 71% cov 100% (n=21; c/i/r 15/6/0) | 5% cov 100% (n=21; c/i/r 1/20/0) | 14% cov 100% (n=21; c/i/r 3/18/0) | 90% cov 100% (n=21; c/i/r 19/2/0) | **45%** cov 100% (n=84; c/i/r 38/46/0) |

### By text (one text = one work · version · language)

**haiku**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 50% | 100% | 0 | — | 0 | 2 | wrong_passage 1, other_script 1 |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 45% | 100% | 0 | — | 19 | 25 | edition_variant 8, paraphrase 11, wrong_passage 11, other_script 6, addition 1, wrong_locus 5, hedge 1, wrong_verdict 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| haiku | 84 | 16,080 | 6,811 |
| **total** | 84 | 16,080 | 6,811 |
