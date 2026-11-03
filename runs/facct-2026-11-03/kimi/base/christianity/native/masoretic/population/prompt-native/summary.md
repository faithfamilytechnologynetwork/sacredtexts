| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| kimi | 90% cov 100% (n=21; c/i/r 19/2/0; minor/major 0/2) | 14% cov 100% (n=21; c/i/r 3/18/0; minor/major 8/10) | 71% cov 100% (n=21; c/i/r 15/6/0; minor/major 6/0) | 81% cov 100% (n=21; c/i/r 17/4/0; minor/major 0/4) | **64%** cov 100% (c/i/r 54/30/0; minor/major 14/16) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| kimi | cite_passage | 2 | 0 | 2 | wrong_locus 2 |
| kimi | complete_unit | 18 | 8 | 10 | edition_variant 1, paraphrase 5, wrong_passage 10, omission 2 |
| kimi | retrieve_quote | 6 | 6 | 0 | edition_variant 3, paraphrase 3, addition 1 |
| kimi | verify_source | 4 | 0 | 4 | wrong_verdict 4 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| kimi | Christianity | 90% cov 100% (n=21; c/i/r 19/2/0) | 14% cov 100% (n=21; c/i/r 3/18/0) | 71% cov 100% (n=21; c/i/r 15/6/0) | 81% cov 100% (n=21; c/i/r 17/4/0) | **64%** cov 100% (n=84; c/i/r 54/30/0) |

### By text (one text = one work · version · language)

**kimi**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 50% | 100% | 0 | — | 1 | 1 | paraphrase 1, wrong_passage 1 |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 65% | 100% | 0 | — | 13 | 15 | edition_variant 4, paraphrase 7, wrong_passage 9, omission 2, addition 1, wrong_locus 2, wrong_verdict 4 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| kimi | 84 | 13,128 | 10,920 |
| **total** | 84 | 13,128 | 10,920 |
