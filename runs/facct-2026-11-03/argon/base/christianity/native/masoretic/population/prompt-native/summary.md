| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| argon | 100% cov 100% (n=21; c/i/r 21/0/0; minor/major 0/0) | 76% cov 100% (n=21; c/i/r 16/5/0; minor/major 5/0) | 62% cov 100% (n=21; c/i/r 13/8/0; minor/major 8/0) | 95% cov 100% (n=21; c/i/r 20/1/0; minor/major 0/1) | **83%** cov 100% (c/i/r 70/14/0; minor/major 13/1) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| argon | complete_unit | 5 | 5 | 0 | edition_variant 2, paraphrase 2, omission 1 |
| argon | retrieve_quote | 8 | 8 | 0 | diacritic_only 1, edition_variant 5, paraphrase 2 |
| argon | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| argon | Christianity | 100% cov 100% (n=21; c/i/r 21/0/0) | 76% cov 100% (n=21; c/i/r 16/5/0) | 62% cov 100% (n=21; c/i/r 13/8/0) | 95% cov 100% (n=21; c/i/r 20/1/0) | **83%** cov 100% (n=84; c/i/r 70/14/0) |

### By text (one text = one work · version · language)

**argon**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 75% | 100% | 0 | — | 1 | 0 | paraphrase 1 |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 84% | 100% | 0 | — | 12 | 1 | diacritic_only 1, edition_variant 7, paraphrase 3, omission 1, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| argon | 84 | 11,410 | 4,525 |
| **total** | 84 | 11,410 | 4,525 |
