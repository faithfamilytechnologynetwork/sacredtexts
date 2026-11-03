| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| fable | 90% cov 100% (n=21; c/i/r 19/2/0; minor/major 0/2) | 100% cov 100% (n=21; c/i/r 21/0/0; minor/major 0/0) | 95% cov 100% (n=21; c/i/r 20/1/0; minor/major 1/0) | 94% cov 81% (n=21; c/i/r 16/1/4; minor/major 0/1) | **95%** cov 95% (c/i/r 76/4/4; minor/major 1/3) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| fable | cite_passage | 2 | 0 | 2 | no_citation 2 |
| fable | complete_unit | 0 | 0 | 0 | addition 3 |
| fable | retrieve_quote | 1 | 1 | 0 | edition_variant 1 |
| fable | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| fable | Christianity | 90% cov 100% (n=21; c/i/r 19/2/0) | 100% cov 100% (n=21; c/i/r 21/0/0) | 95% cov 100% (n=21; c/i/r 20/1/0) | 94% cov 81% (n=21; c/i/r 16/1/4) | **95%** cov 95% (n=84; c/i/r 76/4/4) |

### By text (one text = one work · version · language)

**fable**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 100% | 100% | 0 | — | 0 | 0 | — |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 95% | 95% | 4 | — | 1 | 3 | edition_variant 1, addition 3, no_citation 2, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| fable | 84 | 16,248 | 11,424 |
| **total** | 84 | 16,248 | 11,424 |
