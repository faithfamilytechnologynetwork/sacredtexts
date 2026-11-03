| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| kimi | 90% cov 100% (n=21; c/i/r 19/2/0; minor/major 0/2) | 29% cov 100% (n=21; c/i/r 6/15/0; minor/major 6/9) | 57% cov 100% (n=21; c/i/r 12/9/0; minor/major 8/1) | 100% cov 100% (n=21; c/i/r 21/0/0; minor/major 0/0) | **69%** cov 100% (c/i/r 58/26/0; minor/major 14/12) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| kimi | cite_passage | 2 | 0 | 2 | no_citation 2 |
| kimi | complete_unit | 15 | 6 | 9 | edition_variant 2, paraphrase 4, wrong_passage 9, addition 2 |
| kimi | retrieve_quote | 9 | 8 | 1 | edition_variant 5, near_copy 1, paraphrase 1, wrong_passage 1, omission 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| kimi | Christianity | 90% cov 100% (n=21; c/i/r 19/2/0) | 29% cov 100% (n=21; c/i/r 6/15/0) | 57% cov 100% (n=21; c/i/r 12/9/0) | 100% cov 100% (n=21; c/i/r 21/0/0) | **69%** cov 100% (n=84; c/i/r 58/26/0) |

### By text (one text = one work · version · language)

**kimi**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 50% | 100% | 0 | — | 1 | 1 | near_copy 1, wrong_passage 1 |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 70% | 100% | 0 | — | 13 | 11 | edition_variant 7, paraphrase 5, wrong_passage 9, omission 1, addition 2, no_citation 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| kimi | 84 | 13,819 | 6,708 |
| **total** | 84 | 13,819 | 6,708 |
