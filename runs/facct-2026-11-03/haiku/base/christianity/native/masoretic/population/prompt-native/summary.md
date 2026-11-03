| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| haiku | 65% cov 95% (n=21; c/i/r 13/7/1; minor/major 0/7) | 6% cov 86% (n=21; c/i/r 1/17/3; minor/major 1/16) | 10% cov 100% (n=21; c/i/r 2/19/0; minor/major 10/9) | 62% cov 76% (n=21; c/i/r 10/6/5; minor/major 0/6) | **35%** cov 89% (c/i/r 26/49/9; minor/major 11/38) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| haiku | cite_passage | 7 | 0 | 7 | wrong_locus 3, hedge 1, no_citation 3 |
| haiku | complete_unit | 17 | 1 | 16 | paraphrase 1, wrong_passage 12, other_script 4, addition 1 |
| haiku | retrieve_quote | 19 | 10 | 9 | edition_variant 2, paraphrase 8, wrong_passage 9, addition 1 |
| haiku | verify_source | 6 | 0 | 6 | wrong_verdict 6 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| haiku | Christianity | 65% cov 95% (n=21; c/i/r 13/7/1) | 6% cov 86% (n=21; c/i/r 1/17/3) | 10% cov 100% (n=21; c/i/r 2/19/0) | 62% cov 76% (n=21; c/i/r 10/6/5) | **35%** cov 89% (n=84; c/i/r 26/49/9) |

### By text (one text = one work · version · language)

**haiku**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 25% | 100% | 0 | — | 0 | 3 | wrong_passage 2, wrong_locus 1 |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 35% | 89% | 9 | — | 11 | 35 | edition_variant 2, paraphrase 9, wrong_passage 19, other_script 4, addition 2, wrong_locus 2, hedge 1, no_citation 3, wrong_verdict 6 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| haiku | 84 | 13,395 | 21,560 |
| **total** | 84 | 13,395 | 21,560 |
