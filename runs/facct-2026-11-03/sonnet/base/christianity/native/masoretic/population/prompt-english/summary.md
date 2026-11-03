| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sonnet | 81% cov 100% (n=21; c/i/r 17/4/0; minor/major 0/4) | 86% cov 100% (n=21; c/i/r 18/3/0; minor/major 0/3) | 57% cov 100% (n=21; c/i/r 12/9/0; minor/major 6/3) | 100% cov 38% (n=21; c/i/r 8/0/13; minor/major 0/0) | **77%** cov 85% (c/i/r 55/16/13; minor/major 6/10) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sonnet | cite_passage | 4 | 0 | 4 | hedge 4 |
| sonnet | complete_unit | 3 | 0 | 3 | wrong_passage 3, addition 18 |
| sonnet | retrieve_quote | 9 | 6 | 3 | edition_variant 2, paraphrase 4, other_script 3, addition 5 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sonnet | Christianity | 81% cov 100% (n=21; c/i/r 17/4/0) | 86% cov 100% (n=21; c/i/r 18/3/0) | 57% cov 100% (n=21; c/i/r 12/9/0) | 100% cov 38% (n=21; c/i/r 8/0/13) | **77%** cov 85% (n=84; c/i/r 55/16/13) |

### By text (one text = one work · version · language)

**sonnet**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 75% | 100% | 0 | — | 0 | 1 | other_script 1, addition 1 |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 78% | 84% | 13 | — | 6 | 9 | edition_variant 2, paraphrase 4, wrong_passage 3, other_script 2, addition 22, hedge 4 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sonnet | 84 | 16,248 | 20,536 |
| **total** | 84 | 16,248 | 20,536 |
