| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| terra | 95% cov 100% (n=21; c/i/r 20/1/0; minor/major 0/1) | 62% cov 100% (n=21; c/i/r 13/8/0; minor/major 6/2) | 57% cov 100% (n=21; c/i/r 12/9/0; minor/major 9/0) | 95% cov 100% (n=21; c/i/r 20/1/0; minor/major 0/1) | **77%** cov 100% (c/i/r 65/19/0; minor/major 15/4) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| terra | cite_passage | 1 | 0 | 1 | no_citation 1 |
| terra | complete_unit | 8 | 6 | 2 | edition_variant 5, paraphrase 1, wrong_passage 2 |
| terra | retrieve_quote | 9 | 9 | 0 | edition_variant 8, paraphrase 1 |
| terra | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| terra | Christianity | 95% cov 100% (n=21; c/i/r 20/1/0) | 62% cov 100% (n=21; c/i/r 13/8/0) | 57% cov 100% (n=21; c/i/r 12/9/0) | 95% cov 100% (n=21; c/i/r 20/1/0) | **77%** cov 100% (n=84; c/i/r 65/19/0) |

### By text (one text = one work · version · language)

**terra**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 50% | 100% | 0 | — | 2 | 0 | paraphrase 2 |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 79% | 100% | 0 | — | 13 | 4 | edition_variant 13, wrong_passage 2, no_citation 1, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| terra | 84 | 11,723 | 5,138 |
| **total** | 84 | 11,723 | 5,138 |
