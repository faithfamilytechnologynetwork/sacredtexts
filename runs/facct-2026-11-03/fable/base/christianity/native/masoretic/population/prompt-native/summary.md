| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| fable | 95% cov 100% (n=21; c/i/r 20/1/0; minor/major 0/1) | 100% cov 100% (n=21; c/i/r 21/0/0; minor/major 0/0) | 86% cov 100% (n=21; c/i/r 18/3/0; minor/major 3/0) | 89% cov 86% (n=21; c/i/r 16/2/3; minor/major 0/2) | **93%** cov 96% (c/i/r 75/6/3; minor/major 3/3) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| fable | cite_passage | 1 | 0 | 1 | hedge 1 |
| fable | complete_unit | 0 | 0 | 0 | addition 11 |
| fable | retrieve_quote | 3 | 3 | 0 | edition_variant 2, paraphrase 1 |
| fable | verify_source | 2 | 0 | 2 | wrong_verdict 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| fable | Christianity | 95% cov 100% (n=21; c/i/r 20/1/0) | 100% cov 100% (n=21; c/i/r 21/0/0) | 86% cov 100% (n=21; c/i/r 18/3/0) | 89% cov 86% (n=21; c/i/r 16/2/3) | **93%** cov 96% (n=84; c/i/r 75/6/3) |

### By text (one text = one work · version · language)

**fable**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 75% | 100% | 0 | — | 1 | 0 | edition_variant 1, addition 1 |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 94% | 96% | 3 | — | 2 | 3 | edition_variant 1, paraphrase 1, addition 10, hedge 1, wrong_verdict 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| fable | 84 | 13,563 | 18,223 |
| **total** | 84 | 13,563 | 18,223 |
